# Linkwort

Linkwort is a Markdown linter.

## Features

Linkwort will check Markdown files for the following issues:

- Lines too long.  By default linkwork will raise an error for lines
  longer than 80 characters, but the maximum length is configurable.

- Trailing whitespace.  Linkwort will not raise errors for Markdown
  hard line breaks (two spaces at the end of a line).

- Hard tabs instead of spaces.

- Missing reference links.  If you define a link such as `[link][1]`,
  linkwort will raise an error if you don't define a reference named
  `1` elsewhere in the document.

In its default mode of operation, linkwort will not perform lint
checks in code blocks.  You can override this behavior with the
`--lint-in-code` (`-C`) command line option.

You can disable lint checking in portions of a document by bracketing
the section with `<!-- lint:disable -->`/`<!-- lint:enable -->`.

## Usage

    usage: linkwort [-h] [--list-rules] [--fail-fast] [--lint-in-code]
                    [--include-rules RULEID] [--exclude-rules RULEID]
                    [--max-line-length MAX_LINE_LENGTH] [-v] [-d]
                    [input [input ...]]

    positional arguments:
      input

    optional arguments:
      -h, --help            show this help message and exit
      --list-rules          List available linter rules and exit

    Linting options:
      --fail-fast, -F       Fail on first error
      --lint-in-code, -C    Run lint in code blocks
      --include-rules RULEID, -i RULEID
                            Only run named rules
      --exclude-rules RULEID, -x RULEID
                            Do not run the named rules
      --max-line-length MAX_LINE_LENGTH, -m MAX_LINE_LENGTH

    Logging options:
      -v, --verbose
      -d, --debug

## Contributing

Submit comments, suggestions, and bug reports using the [issue
tracker][].

You may submit changes as a GitHub [pull request][].  Please limit
pull requests to a single commit, and ensure that:

- Your commit message accurately describes the change
- You have added tests for any new features
- Your changes pass the unit tests

[issue tracker]: https://github.com/larsks/linkwort/issues
[pull request]: https://github.com/larsks/linkwort/pulls

## License

Linkwort, a Markdown linter  
Copyright (C) 2017 Lars Kellogg-Stedman <lars@oddbit.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
