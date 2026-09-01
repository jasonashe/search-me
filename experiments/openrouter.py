# -*- coding: utf-8 -*-
"""Minimal OpenRouter client with spend tracking."""
import json
import os
import re
import threading
import urllib.error
import urllib.request

LEDGER = 'experiments/spend.json'
_lock = threading.Lock()


def key():
    for line in open('api-keys.txt', encoding='utf-8'):
        m = re.search(r'sk-or-v1-[A-Za-z0-9]+', line)
        if m:
            return m.group(0)
    raise SystemExit('no OpenRouter key')


def record(model, usage, note):
    with _lock:
        led = json.load(open(LEDGER, encoding='utf-8')) if os.path.exists(LEDGER) \
            else {'total': 0.0, 'runs': []}
        cost = float(usage.get('cost') or 0.0)
        led['total'] = round(led['total'] + cost, 6)
        led['runs'].append({'model': model, 'note': note, 'cost': cost,
                            'in': usage.get('prompt_tokens'),
                            'out': usage.get('completion_tokens')})
        json.dump(led, open(LEDGER, 'w', encoding='utf-8'), indent=1)
        return led['total']


def chat(model, messages, note='', max_tokens=8000, temperature=0.0):
    body = json.dumps({'model': model, 'messages': messages,
                       'max_tokens': max_tokens, 'temperature': temperature,
                       'usage': {'include': True}}).encode()
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions', data=body,
        headers={'Authorization': f'Bearer {key()}',
                 'Content-Type': 'application/json'})
    try:
        out = json.load(urllib.request.urlopen(req, timeout=600))
    except urllib.error.HTTPError as e:
        raise SystemExit(f'{model}: {e.code} {e.read()[:500]}')
    total = record(model, out.get('usage') or {}, note)
    choice = (out.get('choices') or [{}])[0]
    msg = choice.get('message') or {}
    text = msg.get('content') or msg.get('reasoning') or ''
    return text, total
