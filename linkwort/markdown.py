import re

class Patterns(object):
    header = r'^#+.*$'
    fence = r'^(`{3}|\~{3})'
    block_code = r'^ {4}'
    block_quote = r'^ *> '
