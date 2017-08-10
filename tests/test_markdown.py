import unittest
import pytest
import linkwort.lint
import linkwort.exceptions

class TestMarkdown(unittest.TestCase):
    def setUp(self):
        self.m = linkwort.lint.MarkdownLint(fail_fast=True)

    def test_no_problems(self):
        text = (
            'This is a simple markdown document\n'
            'with no problems.'
        )

        assert self.m.parse(text) == []

    def test_long_line(self):
        text = 'x' * 90
        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            self.m.parse(text)

        assert err.value.ruleid == 'max-line-length'

    def test_long_line_exclude_rule(self):
        '''test that when we exclude a rule, that rule is skipped'''
        text = 'x' * 90
        m = linkwort.lint.MarkdownLint(fail_fast=True,
                                       exclude_rules=['max-line-length'])
        assert m.parse(text) == []

    def test_long_line_include_rule(self):
        '''test that when we include a rule, only that rule is checked'''
        text = (
            'x' * 90 + '\n'
            + '\tthis line has a tab'
        )

        m = linkwort.lint.MarkdownLint(include_rules=['hard-tabs'])
        v = m.parse(text)

        assert len(v) == 1
        assert v[0].ruleid == 'hard-tabs'

    def test_long_line_masked(self):
        '''test that we do not check a section of a document that has
        been marked with disable/enable tokens'''
        text = (
            '<!-- lint:disable -->\n'
            + 'x' * 90 + '\n'
            + '<!-- lint:enable -->')
        assert self.m.parse(text) == []

    def test_long_line_code_block(self):
        '''test that linting does not happen by default in
        indented code blocks'''
        text = (
            'Before code block\n'
            + '    ' + 'x' * 90 + '\n'
            + 'After code block.'
        )

        assert self.m.parse(text) == []

    def test_long_line_linted_code_block(self):
        '''test that when we enable linting in code blocks that a long
        line in a code block *will* cause an error'''
        text = (
            'Before code block\n'
            + '    ' + 'x' * 90 + '\n'
            + 'After code block.'
        )
        m = linkwort.lint.MarkdownLint(fail_fast=True,
                                       lint_in_code=True)
        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            m.parse(text)

        assert err.value.ruleid == 'max-line-length'

    def test_long_line_fenced_block(self):
        '''test that linting does not happen by default in
        fenced code blocks'''
        text = (
            'Before code block\n'
            + '```\n'
            + 'x' * 90 + '\n'
            + '```\n'
            + 'After code block.'
        )

        assert self.m.parse(text) == []

    def test_hard_tabs(self):
        text = '\tA line with a hard tab.'

        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            self.m.parse(text)

        assert err.value.ruleid == 'hard-tabs'

    def test_trailing_whitespace(self):
        text = 'A line with a trailing whitespace. '

        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            self.m.parse(text)

        assert err.value.ruleid == 'trailing-whitespace'

    def test_line_break(self):
        '''a markdown hard line break (two spaces at the end of a line) should
        not trigger a trailing-whitespace error.'''
        text = 'A line with a hard line break.  '

        assert self.m.parse(text) == []

    def test_link(self):
        text = (
            'Text with a reference [link][].\n'
            + '[link]: http://google.com/'
        )

        assert self.m.parse(text) == []

    def test_missing_link(self):
        '''test that the linter raises an error when there is a reference used
        without a corresponding reference definition'''
        text = 'Text with a missing reference [link][].'

        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            self.m.parse(text)

        assert err.value.ruleid == 'undefined-reference'

