from __future__ import print_function

import argparse
import logging
import sys

import linkwort.lint
import linkwort.exceptions

LOG = logging.getLogger(__name__)


def parse_args(argv=sys.argv[1:]):
    p = argparse.ArgumentParser()

    g = p.add_argument_group('Linting options')
    g.add_argument('--fail-fast', '-F',
                   action='store_true',
                   help='Fail on first error')
    g.add_argument('--lint-in-code', '-C',
                   action='store_true',
                   help='Run lint in code blocks')
    g.add_argument('--include-rules', '-i',
                   action='append',
                   metavar='RULEID',
                   default=[],
                   help='Only run named rules')
    g.add_argument('--exclude-rules', '-x',
                   action='append',
                   metavar='RULEID',
                   default=[],
                   help='Do not run the named rules')
    g.add_argument('--max-line-length', '-m',
                   type=int,
                   default=80)

    g = p.add_argument_group('Logging options')
    g.add_argument('-v', '--verbose',
                   action='store_const',
                   const='INFO',
                   dest='loglevel')
    g.add_argument('-d', '--debug',
                   action='store_const',
                   const='DEBUG',
                   dest='loglevel')

    p.add_argument('input',
                   nargs='*',
                   default=['-'])

    p.set_defaults(loglevel='WARNING')

    return p.parse_args(argv)


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    logging.basicConfig(level=args.loglevel)

    m = linkwort.lint.MarkdownLint(
        fail_fast=args.fail_fast,
        lint_in_code=args.lint_in_code,
        include_rules = args.include_rules,
        exclude_rules = args.exclude_rules,
        max_line_length=args.max_line_length)

    ret = 0
    try:
        for filename in args.input:
            if filename == '-':
                filename = '<stdin>'

            LOG.info('processing %s', filename)

            with (
                    sys.stdin if filename == '<stdin>'
                    else open(filename, 'r')
            ) as fd:

                violations = m.parse(fd, filename=filename)

                for v in violations:
                    ret += 1
                    print('{}: {}...'.format(v, v.text[:40]))
    except linkwort.exceptions.RuleViolation as v:
        ret += 1
        print('{}: {}...'.format(v, v.text[:40]))

    return ret
