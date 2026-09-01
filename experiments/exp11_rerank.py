# -*- coding: utf-8 -*-
"""Experiment 11 — can a cheap model rerank the candidate list?

exp09 found the ceiling: 84% of the gold quotes are somewhere in the top 400
candidates, but only 58% are in the top 30.  The passages are being retrieved
and then buried.  A reranker is the standard fix, and the economics work here
because the query set is closed: one long-context call per paragraph, 426 calls
total, done once at build time.

What is under test is whether a cheap model can judge Tibetan scholastic
relevance well enough to promote the right passages.  If it cannot, this is a
negative result worth having, and the money stops.
"""
import concurrent.futures
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
sys.path.insert(0, HERE)
import gold as G                                             # noqa: E402
import openrouter as OR                                      # noqa: E402
import pack                                                  # noqa: E402

VIEWER = '/Users/tegchok/སྐབས་དང་པོ།-viewer'
TOP, SNIPPET = 100, 700

INSTRUCTIONS = """You are helping a Tibetan Buddhist scholar working on \
སྐབས་དང་པོའི་སྤྱི་དོན།, the Sera Jey monastic textbook on the Abhisamayālaṃkāra.

You are given ONE paragraph of that text, then a numbered list of PASSAGES found \
in a corpus of commentaries. Score how much each passage would help a scholar \
explain the paragraph.

  3 — directly bears on it: states the position the paragraph states, or the one \
it refutes, or disagrees with it, or supplies the sūtra/kārikā/lemma the paragraph cites
  2 — the same question discussed elsewhere; useful context
  1 — shares vocabulary but is a different discussion
  0 — unrelated

Most passages are 0 or 1. Be strict: a 3 means a scholar would actually quote it.

Reply with JSON only, no other text: [{"id": 1, "s": 0}, {"id": 2, "s": 3}, ...] \
covering every id given."""


def build_prompt(paragraph, cands):
    lines = [f'PARAGRAPH:\n{paragraph}\n\nPASSAGES:']
    for i, c in enumerate(cands, 1):
        lines.append(f"[{i}] ({c['author']} · {c['title']})\n"
                     f"{c['context'][:SNIPPET]}")
    return '\n\n'.join(lines)


def parse(text, n):
    if not text:
        return {}
    m = re.search(r'\[.*\]', text, re.S)
    if not m:
        return {}
    try:
        rows = json.loads(m.group(0))
    except json.JSONDecodeError:
        rows = []
        for mm in re.finditer(r'\{[^{}]*"id"\s*:\s*(\d+)[^{}]*"s"\s*:\s*(\d+)', text):
            rows.append({'id': int(mm.group(1)), 's': int(mm.group(2))})
    return {int(r['id']): int(r['s']) for r in rows
            if isinstance(r, dict) and 'id' in r and 's' in r
            and 1 <= int(r['id']) <= n}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    held_only = '--held-only' in sys.argv
    models = args or ['google/gemini-2.5-flash-lite', 'qwen/qwen3.7-flash']
    R = pack.Retrievers()
    paras = {p['id']: p['text'] for p in json.load(
        open(os.path.join(VIEWER, 'app/data/text.json'),
             encoding='utf-8'))['paragraphs']}
    truth = G.load()
    pids = G.HELD_OUT if held_only else G.TUNE + G.HELD_OUT

    cands = {pid: R.candidates(pid, paras[pid], top=TOP) for pid in pids}
    print(f'{len(pids)} paragraphs, {TOP} candidates each')

    def run(model, pid):
        prompt = build_prompt(paras[pid], cands[pid])
        text, total = OR.chat(model, [
            {'role': 'system', 'content': INSTRUCTIONS},
            {'role': 'user', 'content': prompt}],
            note=f'rerank {pid}', max_tokens=6000)
        return pid, parse(text, len(cands[pid])), total

    results = {}
    for model in models:
        scores = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            for pid, got, total in ex.map(lambda p: run(model, p), pids):
                scores[pid] = got
                print(f'  {model.split("/")[-1]:<24} {pid:>5}  '
                      f'{len(got):>3} scored   running ${total:.3f}', flush=True)
        results[model] = scores

    def measure(split, scores):
        sub = [q for q in truth if q['paragraph'] in split]
        out = {}
        for label in ('before', 'after'):
            hits = {20: 0, 30: 0, 50: 0}
            for pid in split:
                order = list(range(len(cands[pid])))
                if label == 'after' and scores.get(pid):
                    s = scores[pid]
                    order.sort(key=lambda i: (-s.get(i + 1, 0), i))
                for q in (x for x in sub if x['paragraph'] == pid):
                    rank = None
                    for r, i in enumerate(order, 1):
                        c = cands[pid][i]
                        if c['file'] == q['file'] and \
                           abs(c['offset'] - q['offset']) <= 2400:
                            rank = r
                            break
                    for b in hits:
                        if rank and rank <= b:
                            hits[b] += 1
            out[label] = {b: 100 * hits[b] / len(sub) for b in hits}
        return out

    out_path = 'experiments/exp11_rerank.json'
    print('\n\nrecall before and after reranking\n')
    print(f'{"model":<30}{"split":<11}' +
          ''.join(f'{"@" + str(b):>18}' for b in (20, 30, 50)))
    for model, scores in results.items():
        splits = (('held out', G.HELD_OUT),) if held_only else \
            (('tune', G.TUNE), ('held out', G.HELD_OUT))
        for name, split in splits:
            m = measure(split, scores)
            print(f'{model.split("/")[-1]:<30}{name:<11}' + ''.join(
                f'{m["before"][b]:>8.0f}% ->{m["after"][b]:>6.0f}%'
                for b in (20, 30, 50)))
    prev = json.load(open(out_path, encoding='utf-8')) \
        if os.path.exists(out_path) else {}
    prev.update({m: {p: s for p, s in v.items()} for m, v in results.items()})
    json.dump(prev, open(out_path, 'w', encoding='utf-8'))


if __name__ == '__main__':
    main()
