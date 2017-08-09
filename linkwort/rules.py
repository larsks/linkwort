from __future__ import print_function

import re
from linkwort.exceptions import RuleViolation

re_reflink = re.compile(r'\[(?P<label>[^]]+)\]\s*\[(?P<ref>[^]]*)\]')
re_reference = re.compile('\s*\[(?P<ref>[^]]+)\]:\s+(?P<url>.*)')


def rule(ruleid, ruletags=None):

    if ruletags is None:
        ruletags = ['inline']

    def outer(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RuleViolation as err:
                if err.ruleid is None:
                    err.ruleid = ruleid
                raise err

        inner.ruleid = ruleid
        inner.ruletags = ruletags
        return inner
    return outer


@rule('max-line-length')
def max_line_length(filename, ln, line, ctx):
    if len(line) > 80:
        raise RuleViolation(None, filename, ln, line)


@rule('hard-tabs')
def hard_tabs(filename, ln, line, ctx):
    if '\t' in line:
        raise RuleViolation(None, filename, ln, line)


@rule('trailing-whitespace', ruletags=['inline', 'code'])
def trailing_whitespace(filename, ln, line, ctx):
    if line.endswith(' '):
        raise RuleViolation(None, filename, ln, line)


@rule('collect-links', ruletags=['chunk'])
def collect_links(filename, ln, chunk, ctx):
    reflinks = re_reflink.findall(chunk)
    for label, ref in reflinks:
        if 'reflinks' not in ctx:
            ctx['reflinks'] = set()

        ref = ref if ref else label
        ctx['reflinks'].add(ref.lower())


@rule('collect-refs')
def collect_refs(filename, ln, line, ctx):
    mo = re_reference.match(line)
    if mo:
        if 'references' not in ctx:
            ctx['references'] = set()

        ctx['references'].add(mo.group('ref').lower())


@rule('missing-ref-link', ruletags=['atend'])
def missing_ref_link(filename, ln, line, ctx):
    refs_wanted = ctx.get('reflinks', set())
    refs_defined = ctx.get('references', set())

    refs_missing = refs_wanted - refs_defined
    if refs_missing:
        raise RuleViolation(None, filename, ln, ', '.join(refs_missing))
