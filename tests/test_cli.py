import os
import pytest
import shutil
import six
import sys
import tempfile
import unittest

import linkwort.main
import linkwort.exceptions

testfiles = {
    'simple.md': 'This is a simple document.\n',
    'longline.md': 'This file has a long line.\n' + 'x' * 90 + '\n',
    'codeblock.md': (
        'Before a codeblock.\n' +
        '```\n' + 'x' * 90 + '\n```\n' +
        'After a codeblock'
    )
}

class TestMarkdown(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.mkdtemp(prefix='workspace')

        for filename, content in testfiles.items():
            path = os.path.join(self.workspace, filename)
            with open(path, 'w') as fd:
                fd.write(content)

    def tearDown(self):
        shutil.rmtree(self.workspace)

    def test_missing_file(self):
        ret = linkwort.main.main(
            argv=['__does_not_exist__'])

        assert ret == 1

    def test_good(self):
        ret = linkwort.main.main(
            argv=[os.path.join(self.workspace, 'simple.md')])

        assert ret == 0

    def test_good_with_shorter_max_line(self):
        ret = linkwort.main.main(
            argv=['-m', '10',
                  os.path.join(self.workspace, 'simple.md')])

        assert ret == 1

    def test_longline(self):
        ret = linkwort.main.main(
            argv=[os.path.join(self.workspace, 'longline.md')])

        assert ret == 1

    def test_longline_fast(self):
        ret = linkwort.main.main(
            argv=['-F',
                  os.path.join(self.workspace, 'longline.md')])

        assert ret == 1

    def test_codeblock(self):
        ret = linkwort.main.main(
            argv=[os.path.join(self.workspace, 'codeblock.md')])

        assert ret == 0

    def test_codeblock_linted(self):
        ret = linkwort.main.main(
            argv=['-C',
                  os.path.join(self.workspace, 'codeblock.md')])

        assert ret == 1

    def test_list_rules(self):
        sys.stdout = six.StringIO()
        rules = [rule['ruleid'] for rule in linkwort.rules.rules
                 if not rule.get('always_run')]
        ret = linkwort.main.main(
            argv=['--list-rules'])

        assert ret == None
        assert sys.stdout.getvalue().strip() == '\n'.join(rules).strip()
