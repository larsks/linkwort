from __future__ import print_function

import re
from functools import wraps
from linkwort.exceptions import RuleViolation

re_reflink = re.compile(r'\[(?P<label>[^]]+)\]\s*\[(?P<ref>[^]]*)\]')
re_reference = re.compile('\s*\[(?P<ref>[^]]+)\]:\s+(?P<url>.*)')
re_linebreak = re.compile('\S  $')

# The @rule decorator will register rule functions in this list in
# the order in which they are defined.
rules = []


def rule(ruleid, ruletags=None, always_run=False):
    '''register a rule function in the global rules list'''
    if ruletags is None:
        ruletags = ['inline']

    def outer(rulefunc):
        @wraps(rulefunc)
        def inner(*args, **kwargs):
            try:
                return rulefunc(*args, **kwargs)
            except RuleViolation as err:
                if err.ruleid is None:
                    err.ruleid = ruleid
                raise err

        rules.append({'ruleid': ruleid,
                      'ruletags': ruletags,
                      'rulefunc': inner,
                      'always_run': always_run})
        return inner
    return outer


@rule('max-line-length')
def max_line_length(filename, ln, line, ctx):
    '''raise a RuleViolation if the given line is longer than
    80 characters'''
    if len(line) > ctx.get('max_line_length', 80):
        raise RuleViolation(None, filename, ln, line)


@rule('hard-tabs')
def hard_tabs(filename, ln, line, ctx):
    '''Raise a RuleViolation if the given line contains a tab
    ('\\t', ASCII 09) character'''
    if '\t' in line:
        raise RuleViolation(None, filename, ln, line)


@rule('trailing-whitespace', ruletags=['inline'])
def trailing_whitespace(filename, ln, line, ctx):
    '''Raise a RuleViolation if the given line contains trailing
    whitespace.  Will not raise an error for markdown line breaks (two spaces
    at the end of a line).'''
    if re_linebreak.search(line):
        return

    if line.endswith(' '):
        raise RuleViolation(None, filename, ln, line)


@rule('collect-links', ruletags=['chunk', 'atend'],
      always_run=True)
def collect_links(filename, ln, chunk, ctx):
    '''collect links referenced in the document'''
    reflinks = re_reflink.findall(chunk)
    for label, ref in reflinks:
        if 'reflinks' not in ctx:
            ctx['reflinks'] = set()

        ref = ref if ref else label
        ctx['reflinks'].add(ref.lower())


@rule('collect-refs', always_run=True)
def collect_refs(filename, ln, line, ctx):
    '''collect links defined in the document'''
    mo = re_reference.match(line)
    if mo:
        if 'references' not in ctx:
            ctx['references'] = set()

        ctx['references'].add(mo.group('ref').lower())


@rule('missing-ref-link', ruletags=['atend'])
def missing_ref_link(filename, ln, line, ctx):
    '''raise an error if there are referenced links for which
    no definition was provided'''
    refs_wanted = ctx.get('reflinks', set())
    refs_defined = ctx.get('references', set())

    refs_missing = refs_wanted - refs_defined
    if refs_missing:
        raise RuleViolation(None, filename, ln, ', '.join(refs_missing))
