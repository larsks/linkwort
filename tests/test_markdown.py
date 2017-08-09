import unittest
import pytest
import linkwort.lint
import linkwort.exceptions

class TestMarkdown(unittest.TestCase):

    def test_no_problems(self):
        text = (
            'This is a simple markdown document\n'
            'with no problems.'
        )

        m = linkwort.lint.MarkdownLint()
        assert m.parse(text, fail_fast=True) == []

    def test_long_line(self):
        text = 'x' * 90
        m = linkwort.lint.MarkdownLint()
        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            m.parse(text, fail_fast=True)

        assert err.value.ruleid == 'max-line-length'

    def test_long_line_masked(self):
        text = (
            '<!-- lint:disable -->\n'
            + 'x' * 90 + '\n'
            + '<!-- lint:enable -->')
        m = linkwort.lint.MarkdownLint()
        assert m.parse(text, fail_fast=True) == []

    def test_long_line_code_block(self):
        text = (
            'Before code block\n'
            + '   ' + 'x' * 90 + '\n'
            + 'After code block.'
        )

        m = linkwort.lint.MarkdownLint()
        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            m.parse(text, fail_fast=True)

        assert err.value.ruleid == 'max-line-length'

    def test_hard_tabs(self):
        text = '\tA line with a hard tab.'

        m = linkwort.lint.MarkdownLint()
        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            m.parse(text, fail_fast=True)

        assert err.value.ruleid == 'hard-tabs'

    def test_trailing_whitespace(self):
        text = 'A line with a trailing whitespace. '

        m = linkwort.lint.MarkdownLint()
        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            m.parse(text, fail_fast=True)

        assert err.value.ruleid == 'trailing-whitespace'

    def test_line_break(self):
        '''a markdown hard line break (two spaces at the end of a line) should
        not trigger a trailing-whitespace error.'''
        text = 'A line with a hard line break.  '

        m = linkwort.lint.MarkdownLint()
        assert m.parse(text, fail_fast=True) == []

    def test_missing_link(self):
        text = 'Text with a missing reference [link][].'

        m = linkwort.lint.MarkdownLint()
        with pytest.raises(linkwort.exceptions.RuleViolation) as err:
            m.parse(text, fail_fast=True)

        assert err.value.ruleid == 'missing-ref-link'

