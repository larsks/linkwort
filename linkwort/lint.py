from __future__ import print_function

import logging
import sys
import re
import itertools

from linkwort import rules
from linkwort import exceptions

LOG = logging.getLogger(__name__)

def pp_stripper(src):
    '''strip the trailing newline from all input lines'''
    for ln, line in src:
        if line.endswith('\n'):
            line = line[:-1]

        yield ln, line

def pp_blankline(src):
    '''collapse multiple blank lines into a single blank line'''
    last = None

    for ln, line in src:
        if line == '':
            if last == '':
                continue

        yield ln, line

        last = line

def pp_marker(src):
    '''remove text between lint:disable and lint:enable markers'''
    ignoring = False

    for ln, line in src:
        if ignoring:
            if line.startswith('<!-- lint:enable -->'):
                ignoring = False
                continue
        else:
            if line.startswith('<!-- lint:disable -->'):
                ignoring = True
                continue

            yield ln, line

class MarkdownLint(object):
    def pipeline(self, src):
        for ln, line in pp_blankline(
                pp_marker(
                    pp_stripper(
                        enumerate(src)))):

            yield ln, line

    def run_rules(self, tag, filename, ln, data, ctx):
        for rule in dir(rules):
            rulefunc = getattr(rules, rule)
            if not hasattr(rulefunc, 'ruleid'):
                continue
            if not tag in getattr(rulefunc, 'ruletags', []):
                continue

            rulefunc(filename, ln, data, ctx)

    def parse(self, src, filename='<unknown>'):
        violations = []

        if hasattr(src, 'read'):
            src = src
        elif hasattr(src, 'splitlines'):
            src = src.splitlines()
        else:
            raise ValueError("don't know how to process "
                             "src of type %s" % type(src))

        lastindent = 0
        ctx = {}
        chunk = []
        fenced = None
        for ln, line in self.pipeline(src):
            if fenced:
                if line == 'fenced':
                    fence = False
                continue
            else:
                if line in ['```', '~~~']:
                    fenced = True
                    continue

            if line == '':
                if chunk:
                    chunk_wrapped = ' '.join(chunk)
                    self.run_rules('chunk', filename, ln, chunk_wrapped, ctx)

                chunk = []
                continue

            chunk.append(line)

            indent = sum(1 for _ in
                         itertools.takewhile(lambda x: x == ' ', line))

            # skip code blocks
            if indent >= (lastindent + 4):
                continue

            try:
                self.run_rules('inline', filename, ln, line, ctx)
            except exceptions.RuleViolation as err:
                violations.append(err)

            lastindent = indent

        try:
            self.run_rules('atend', filename, ln, None, ctx)
        except exceptions.RuleViolation as err:
            violations.append(err)

        return violations

if __name__ == '__main__':
    m = MarkdownLint()
    with open(sys.argv[1]) as fd:
        violations = m.parse(fd.read())

    for violation in violations:
        print('%s: %s' % (violation, violation.text))
