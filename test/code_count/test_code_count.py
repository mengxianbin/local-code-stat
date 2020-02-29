import re

from code_count import count, get_data, dump_data
from log import get_logger
from walk import walk, WalkHandler

logger = get_logger()


def test_read_file(path=__file__):
    # Read file content
    #   Use 'rb' option to parse line ending as '\r\n'
    #   Use 'r' to parse as '\n' rather than '\r\n'
    file_in = open(path, 'r')
    text = file_in.read()
    logger.debug(text)
    file_in.close()

    return text


def test_match_first():
    text = test_read_file()
    group = re.match(r'.*?#', text, re.S).group()
    logger.debug(group)


def test_multi_line_string():
    a = 1
    """
     abc
     """
    print(a)
    print("""
        def
        """)
    print('''
         ghi
         ''')
    logger.debug(
        '''
             jk
             ''')
    logger.debug(({((
        '''
        lmn
        '''
    ))}))

    ''
    ""

    print(
        "opq")

    print("rst")

    (
        """
        """,

        # abc

        1,

        [
            '''
            ''',

            # xyz

            2
        ]
    )


def test_match(pattern, string):
    match = re.match(pattern, string, re.S)
    result = match.group() if match else None
    m_count = len(match.groups()) if match else 0
    logger.debug('[Match]: Result={%s}, String={%s}, Pattern={%s}, Count={%d}' % (result, string, pattern, m_count))


def test_search(pattern, string):
    search = re.search(pattern, string, re.S)
    logger.debug('[Search]: {%s}' % search.group() if search else None)


def test_space_character():
    # Test \s
    test_match(r'\s*\n', '\n')


def test_non_greedy():
    # Test ?
    test_match('\s*[_\w].*?\n', test_read_file())


def test_string_lex():
    # Test \'
    test_match(r'.*?\'', "a\\\'b\'c\'d\\\'")
    test_match(r'.*?[^\\]\'', "a\\\'b\'c\'d\\\'")
    test_match(r'.*[^\\]\'', "a\\\'b\'c\'d\\\'")
    test_match(r'.*\'', "a\\\'b\'c\'d\\\'")


def test_string():
    # Test String
    exp = "\'\\s*\\'.*?[^\\\\]\\'\'"
    pattern_1 = r'\s*\'.*?[^\\]\''
    pattern_2 = r'\s*\'.*?[^\\]?\''
    pattern_3 = r'\s*\'(.*?[^\\]\'|\')'
    logger.debug('[exp]: {%s}' % exp)
    test_match(pattern_1, "''")
    test_match(pattern_1, exp)
    test_match(pattern_2, "''")
    test_match(pattern_2, exp)
    test_match(pattern_3, "''")
    test_match(pattern_3, exp)


def test_line_break():
    # Test Line Break
    pattern_list = list()
    exp_list = list()

    exp_list.append(":\n")
    pattern_list.append(r'.*?(?=["\'\(\)\[\]\{\}\n])')
    pattern_list.append(r'.*?\n')
    pattern_list.append(r'.*?[\n]')
    pattern_list.append(r'.*?["\'\n]')

    for pattern in pattern_list:
        logger.debug('')
        for exp in exp_list:
            test_match(pattern, exp)


def test_brackets():
    # Use regex lib

    # # Test (), [] and {}
    #   (): Parentheses
    #   []: Brackets
    #   {}: Braces
    exp = '11(22(abc)33(def, 44 (ghi)55 ) 66) 77'
    pattern_list = list()
    pattern_list.append(r'.*?\((?:[^()]*|(?R))*\)')
    pattern_list.append(r'.*?\((?:[^()]*|(?R))\)')
    pattern_list.append(r'.*?\((?:[^()]*)|(?R)*\)')
    pattern_list.append(r'.*?\([^()]*|(?R)*\)')
    pattern_list.append(r'.*?\(([^()]*|(?R))*\)')
    pattern_list.append(r'\s*\(([^()]*|(?R))*\)')

    # for pattern in pattern_list:
    #     logger.debug(regex.match(pattern, exp))

    pass


def test_alternative_group():
    # Test (|)

    pattern_list = list()
    exp_list = list()

    exp_list.append('abcd')
    exp_list.append('abd')
    pattern_list.append(r'ab|cd')
    pattern_list.append(r'a(b|c)d')

    for pattern in pattern_list:
        logger.debug('')
        for exp in exp_list:
            test_match(pattern, exp)


def test_escape_characters():
    # Test "\\"

    pattern_list = list()
    exp_list = list()

    exp_list.append('""')
    exp_list.append('"\\\\"')
    exp_list.append('"\\\\\\"')
    exp_list.append('"\\ABC\\\\"')
    exp_list.append('"\\\\ABC\\"')
    pattern_list.append(r'\s*"("|.*?[\\\\]*[^\\]")')
    pattern_list.append(r'\s*"("|.*?[^\\]")')
    pattern_list.append(r'\s*"(.*?[^\\]")')
    pattern_list.append(r'\s*"(.*?")')
    pattern_list.append(r'\s*"(.*?[\\\\]*")')
    pattern_list.append(r'\s*"("|.*?[\\\\]*")')
    pattern_list.append(r'\s*"("|.*?[^\\][\\\\]*")')
    pattern_list.append(r'\s*"("|.*?[^\\]*?[\\\\]*")')
    pattern_list.append(r'\s*"(|.*?)"')
    pattern_list.append(r'\s*"(|[^\\]*?)"')
    pattern_list.append(r'\s*"(|([^\\]|\\[^\\])*?(\\\\)*?)"')

    for pattern in pattern_list:
        logger.debug('')
        for exp in exp_list:
            test_match(pattern, exp)


def test_named_group():
    # Test named group

    pattern_list = list()
    exp_list = list()

    exp_list.append('"ABC"')
    exp_list.append("'ABC'")
    exp_list.append("'ABC\"")
    exp_list.append('"ABC\'')
    pattern_list.append(r'(?P<id>"|\')ABC(?P=id)')

    for pattern in pattern_list:
        logger.debug('')
        for exp in exp_list:
            test_match(pattern, exp)


def test_lua_sl_comment():
    pattern_list = list()
    exp_list = list()

    # Test lua single-line comment
    exp_list.append(' --')
    pattern_list.append(r'\s*\-\-.*?(?=\n|())')

    for pattern in pattern_list:
        logger.debug('')
        for exp in exp_list:
            test_match(pattern, exp)


def test_space_line_count():
    pattern_list = list()
    exp_list = list()

    # Test space line count calculation
    exp_list.append('''


    ''')
    pattern_list.append(r'(?=\n)\s*?\n')

    for pattern in pattern_list:
        logger.debug('')
        for exp in exp_list:
            result = re.findall(pattern, exp)
            print(result)


def test_find_all():
    pattern_list = list()
    exp_list = list()

    # Test multiple match groups
    exp_list.append('abacad')
    pattern_list.append(r'a')

    for pattern in pattern_list:
        logger.debug('')
        for exp in exp_list:
            result = re.findall(pattern, exp)
            print(result)


def count_file(path):
    class _Handler(WalkHandler):
        def handle_file(self, file_path, context):
            count(file_path)

    walk(path, _Handler())


def assert_data(path, file_tag, **kwargs):
    count_data = count(path)
    file_data = get_data(count_data, file_tag)

    def assert_log(is_ok, msg):
        logger.info(msg) if is_ok else logger.error(msg)

    logger.critical('\n[Assert] path={%s}' % path)
    for lex_tag, expected in kwargs.items():
        actual = get_data(file_data, lex_tag)
        result = expected == actual
        assert_log(result, '\t[%s] is_ok={%s}, expected={%d}, actual={%d}' % (lex_tag, result, expected, actual))


def test_python():
    # count('python')

    assert_data('python/1.py', 'Python', Space=3, Comment=3, Total=6)
    assert_data('python/2.py', 'Python', Space=7, Comment=6, Code=1, Total=14)
    assert_data('python/3.py', 'Python', Space=2, Comment=1, Total=3)
    assert_data('python/4.py', 'Python', Space=5, Comment=3, Total=8)
    assert_data('python/5.py', 'Python', Space=3, Comment=4, Code=1, Total=8)

    # count_file('python')


def test_java():
    # count('java')

    assert_data('java/1.java', 'Java', Space=3, Comment=3, Total=6)
    assert_data('java/2.java', 'Java', Space=6, Comment=6, Code=3, Total=15)
    assert_data('java/3.java', 'Java', Space=3, Comment=3, Total=6)
    assert_data('java/4.java', 'Java', Space=5, Comment=3, Total=8)
    assert_data('java/5.java', 'Java', Space=2, Comment=1, Code=3, Total=6)

    # count_file('java')


def test_lua():
    # count('lua')

    assert_data('lua/1.lua', 'Lua', Space=5, Comment=3, Code=1, Total=9)
    assert_data('lua/2.lua', 'Lua', Space=1, Comment=2, Total=3)
    assert_data('lua/3.lua', 'Lua', Space=6, Comment=3, Code=1, Total=10)
    assert_data('lua/4.lua', 'Lua', Space=2, Comment=1, Code=2, Total=5)
    assert_data('lua/5.lua', 'Lua', Space=4, Comment=2, Code=5, Total=11)

    # count_file('lua')


def test_root():
    count('../..')


if __name__ == '__main__':
    # test_string()
    # test_line_break()

    # test_read_file()
    # test_match_first()
    # test_multi_line_string()

    # test_python()
    # test_java()
    # test_lua()
    # test_root()

    # test_find_all()
    # test_space_line_count()

    # data = count('../..')
    # data = count('../../code_count.py')
    # data = count('../../config.py')
    # data = count(__file__)
    data = count('../../README.md')

    logger.critical(dump_data(data))

    pass
