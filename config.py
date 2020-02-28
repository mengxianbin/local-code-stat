import logging
import re
from os import path

from dynamic_object import DynamicObject

LOG_LEVEL = logging.DEBUG

LOG_FORMAT = '%(message)s'

OUTPUT = path.join(path.dirname(__file__), 'out')

IGNORED_FOLDERS = {'.git', '.gitee', '.idea', '.vscode', '.svn', 'bin', 'out', 'target', 'trace'}

IGNORED_FILES = {r'.*\.DS_Store'}

PYTHON_LEXER_LIST = []
C_LIKE_LEXER_LIST = []
LUA_LEXER_LIST = []
TEXT_LEXER_LIST = []
FILE_HANDLER_LIST = [
    DynamicObject(tag='Python', path=r'.*\.py$', lexer_list=PYTHON_LEXER_LIST),
    DynamicObject(tag='Java', path=r'.*\.java$', lexer_list=C_LIKE_LEXER_LIST),
    DynamicObject(tag='Lua', path=r'.*\.lua$', lexer_list=LUA_LEXER_LIST),
    DynamicObject(tag='Markdown', path=r'.*\.md$', lexer_list=TEXT_LEXER_LIST),
    DynamicObject(tag='C#', path=r'.*\.cs$', lexer_list=C_LIKE_LEXER_LIST),
    DynamicObject(tag='C', path=r'.*\.(h|c)$', lexer_list=C_LIKE_LEXER_LIST),
    DynamicObject(tag='C++', path=r'.*\.cpp$', lexer_list=C_LIKE_LEXER_LIST),
]

TAG_ALL = 'All'
TAG_TEST = 'Test'

LEX_SPACE = 'Space'
LEX_COMMENT = 'Comment'
LEX_CODE = 'Code'
LEX_TOTAL = 'Total'

FLAG_BRACKETS = 'brackets'
FLAG_CODE = 'code_line_unfinished'

LEX_LIST = {LEX_SPACE, LEX_COMMENT, LEX_CODE, LEX_TOTAL}

PYTHON_LEXER_LIST.extend([
    # Space line
    DynamicObject(tag=LEX_SPACE, rule=r'\s*\n', flags=re.S),

    # Brackets in: () / [] / {}
    DynamicObject(tag=LEX_CODE, rule=r'\s*[\(\[\{][^\(\)\[\]\{\}]*?(?=["\'\(\)\[\]\{\}])', flags=re.S,
                  stack=(FLAG_BRACKETS, 1)),
    # Brackets out: () / [] / {}
    DynamicObject(tag=LEX_CODE, rule=r'\s*[\)\]\}]', flags=re.S, stack=(FLAG_BRACKETS, -1)),

    # Multi-line comment which starts with '''
    DynamicObject(tag=LEX_COMMENT, rule=r'\s*(?P<_1>("|\'){3}).*?(?P=_1)', flags=re.S,
                  condition=(FLAG_BRACKETS, LEX_CODE)),
    # Single-line comment
    DynamicObject(tag=LEX_COMMENT, rule=r'\s*#.*?(?=\n)', flags=re.S),

    # String
    DynamicObject(tag=LEX_CODE, rule=r'\s*(?P<_1>"|\')(|([^\\]|\\.)*?)(?P=_1)', flags=re.S),

    # Code line without strings, multi-line comments or brackets
    DynamicObject(tag=LEX_CODE, rule=r'.*?(?=["\'\(\)\[\]\{\}\n])', flags=re.S),
])

C_LIKE_LEXER_LIST.extend([
    # Space line
    DynamicObject(tag=LEX_SPACE, rule=r'\s*\n', flags=re.S),

    # Brackets in: () / [] / {}
    DynamicObject(tag=LEX_CODE, rule=r'\s*[\(\[\{][^\(\)\[\]\{\}]*?(?=["\'\(\)\[\]\{\}]|//|/\*)', flags=re.S),
    # Brackets out: () / [] / {}
    DynamicObject(tag=LEX_CODE, rule=r'\s*[\)\]\}]', flags=re.S),

    # Multi-line comment which starts with '''
    DynamicObject(tag=LEX_COMMENT, rule=r'\s*/\*.*?\*/', flags=re.S),
    # Single-line comment
    DynamicObject(tag=LEX_COMMENT, rule=r'\s*//.*?(?=\n)', flags=re.S),

    # String or character
    DynamicObject(tag=LEX_CODE, rule=r'\s*(?P<_1>"|\')(|([^\\]|\\.)*?)(?P=_1)', flags=re.S),

    # Code line without strings, multi-line comments or brackets
    DynamicObject(tag=LEX_CODE, rule=r'.*?(?=["\'\(\)\[\]\{\}\n]|//|/\*)', flags=re.S),
])

LUA_LEXER_LIST.extend([
    # Space line
    DynamicObject(tag=LEX_SPACE, rule=r'\s*\n', flags=re.S),

    # Multi-line comment which starts with '''
    DynamicObject(tag=LEX_COMMENT, rule=r'\s*\-\-\[\[.*?\]\]', flags=re.S),
    # Single-line comment
    DynamicObject(tag=LEX_COMMENT, rule=r'\s*\-\-.*?(?=\n)', flags=re.S),

    # String or character
    DynamicObject(tag=LEX_CODE, rule=r'\s*(?P<_1>"|\')(|([^\\]|\\.)*?)(?P=_1)', flags=re.S),
    # Multi-line string
    DynamicObject(tag=LEX_CODE, rule=r'\s*\[\[(|([^\\]|\\.)*?)\]\]', flags=re.S),

    # Brackets in: () / [] / {}
    DynamicObject(tag=LEX_CODE, rule=r'\s*[\(\[\{][^\(\)\[\]\{\}]*?(?=["\'\(\)\[\]\{\}])', flags=re.S),
    # Brackets out: () / [] / {}
    DynamicObject(tag=LEX_CODE, rule=r'\s*[\)\]\}]', flags=re.S),

    # Code line without strings, multi-line comments or brackets
    DynamicObject(tag=LEX_CODE, rule=r'.*?(?=["\'\(\)\[\]\{\}\n])', flags=re.S),
])

TEXT_LEXER_LIST.extend([
    # Any line
    DynamicObject(tag=LEX_TOTAL, rule=r'', flags=re.S),
])
