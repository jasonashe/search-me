# -*- coding: utf-8 -*-
"""Each paragraph's position in the text's own sa bcad.

The viewer already carries a 687-entry outline with levels and the paragraph
each entry opens at, so the outline does not have to be re-derived from the
prose — which was the plan until the outline turned out to be already there.
What is missing is the *path*: section 3 of the rubric wants to say where a
paragraph sits in the divisions of the text, and that means the chain of
ancestors, not the nearest heading.

The path is built by walking the outline in order and keeping a stack by level,
which is the same reconstruction the sidebar does.
"""
import json


def load(text_json):
    doc = json.load(open(text_json, encoding='utf-8'))
    order = {p['id']: i for i, p in enumerate(doc['paragraphs'])}
    entries = [e for e in doc.get('toc') or [] if e.get('paraId')]
    entries.sort(key=lambda e: (order.get(e['paraId'], 0),
                                e.get('level') or 0))

    paths, stack = {}, []
    at = 0
    for i, p in enumerate(doc['paragraphs']):
        while at < len(entries) and order.get(entries[at]['paraId'], 0) <= i:
            e = entries[at]
            level = e.get('level') or 0
            while stack and stack[-1]['level'] >= level:
                stack.pop()
            stack.append({'level': level, 'label': e['label'],
                          'paraId': e['paraId'], 'page': e.get('page')})
            at += 1
        paths[p['id']] = [dict(s) for s in stack]
    return paths


def render(path, width=3):
    """The last `width` steps of the path, deepest last — what a reader needs."""
    return [f"{'  ' * i}{s['label']}" for i, s in enumerate(path[-width:])]
