from __future__ import print_function

import itertools
import logging
import re

from linkwort import rules
from linkwort import exceptions

LOG = logging.getLogger(__name__)

re_fenced = re.compile(r'^(`{3}|~{3})\w*$')
default_max_line_length = 80


class Pipeline(object):
    '''A simple generator pipeline, used to implement filtering
    in the linter.'''

    def __init__(self):
        self.filters = []

    def add_filter(self, filter):
        self.filters.append(filter)

    def process(self, src):
        pipeline = src
        for filter in self.filters:
            pipeline = filter(pipeline)

        return pipeline


class MarkdownLint(object):
    def __init__(self,
                 lint_in_code=False,
                 fail_fast=False,
                 include_rules=None,
                 exclude_rules=None,
                 max_line_length=default_max_line_length):

        include_rules = set(include_rules if include_rules else [])
        exclude_rules = set(exclude_rules if exclude_rules else [])

        self.lint_in_code = lint_in_code
        self.fail_fast = fail_fast
        self.lastindent = 0
        self.include_rules = include_rules
        self.exclude_rules = exclude_rules
        self.max_line_length = max_line_length

        self.pipeline = Pipeline()

        self.pipeline.add_filter(self.pp_stripper)
        self.pipeline.add_filter(self.pp_marker)
        if not lint_in_code:
            self.pipeline.add_filter(self.pp_codeeater)
        self.pipeline.add_filter(self.pp_blankline)

    def pp_stripper(self, src):
        '''strip the trailing newline from all input lines'''
        for ln, line in src:
            if line.endswith('\n'):
                line = line[:-1]

            yield ln, line

    def pp_blankline(self, src):
        '''collapse multiple blank lines into a single blank line'''
        last = None

        for ln, line in src:
            if line == '':
                if last == '':
                    continue

            yield ln, line

            last = line

    def pp_marker(self, src):
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

    def pp_codeeater(self, src):
        '''this processor will filter out fenced and indented code blocks'''
        fenced = None

        for ln, line in src:
            indent = sum(1 for _ in
                         itertools.takewhile(lambda x: x == ' ', line))

            if indent >= self.lastindent + 4:
                continue

            self.lastindent = indent

            if fenced is not None:
                if line == fenced:
                    fenced = None
                continue
            else:
                mo = re_fenced.match(line)
                if mo:
                    fenced = mo.group(1)
                    continue

            yield ln, line

    def run_rules(self, tag, filename, ln, data, ctx):
        for rule in rules.rules:
            if tag not in rule['ruletags']:
                LOG.debug('skipping rule [tag]: %s', rule['ruleid'])
                continue

            if (
                    self.include_rules
                    and rule['ruleid'] not in self.include_rules
                    and not rule['always_run']
            ):
                LOG.debug('skipping rule [include]: %s', rule['ruleid'])
                continue

            if (
                    rule['ruleid'] in self.exclude_rules
                    and not rule['always_run']
            ):
                LOG.debug('skipping rule [exclude]: %s', rule['ruleid'])
                continue

            LOG.debug('running rule: %s', rule['ruleid'])
            rule['rulefunc'](filename, ln, data, ctx)

    def parse(self, src, filename='<unknown>'):
        violations = []

        if hasattr(src, 'read'):
            src = src
        elif hasattr(src, 'splitlines'):
            src = src.splitlines()
        else:
            raise ValueError("don't know how to process "
                             "src of type %s" % type(src))

        ctx = {
            'max_line_length': self.max_line_length,
        }
        chunk = []

        # we need to initialize ln because it is possible for the
        # following loop to execute zero times (e.g., for an empty file,
        # or for a file completely bracketed by disable/enable markers.
        ln = 0
        for ln, line in self.pipeline.process(enumerate(src)):
            LOG.debug('[%03d]: %s', ln, line)

            if line == '':
                if chunk:
                    LOG.debug('running chunk rules')
                    chunk_folded = ' '.join(chunk)
                    self.run_rules('chunk', filename, ln, chunk_folded, ctx)

                chunk = []
                continue

            chunk.append(line)

            try:
                LOG.debug('running inline rules')
                self.run_rules('inline', filename, ln, line, ctx)
            except exceptions.RuleViolation as err:
                if self.fail_fast:
                    raise
                violations.append(err)

        chunk_folded = ' '.join(chunk)
        try:
            LOG.debug('running atend rules')
            self.run_rules('atend', filename, ln, chunk_folded, ctx)
        except exceptions.RuleViolation as err:
            if self.fail_fast:
                raise
            violations.append(err)

        return violations
