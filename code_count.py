import os
import re
from functools import reduce

import config
from dynamic_object import DynamicObject
from log import get_logger
from walk import walk, WalkHandler

logger = get_logger()

"""
Output structure:

# path counter

    # file counter

        # python
        # java
        # markdown

    # dir counter

        # main
        # test

# content counter

    # line counter

        # code
        # comment
        # space line
        # total

"""


def _key(tag):
    try:
        return '_%s' % '_'.join((str(ord(c)) for c in tag))
    except BaseException as e:
        logger.exception(e)


def _tag(key):
    try:
        return ''.join((chr(int(k)) for k in key[1:].split('_')))
    except BaseException as e:
        logger.exception(e)


def add_data(data, tag, increment, remove_zero=False):
    key = _key(tag)
    data[key] = increment if data[key] is None else data[key] + increment
    if remove_zero and data[key] == 0:
        data[key] = None


def remove_data(data, tag):
    key = _key(tag)
    data[key] = None


def get_data(data, tag, default_value=None):
    value = data[_key(tag)]
    return value if value else default_value


def update_data(data, tag, default_value=None):
    key = _key(tag)
    if key in data:
        return data[key]
    else:
        data[key] = default_value
        return default_value


def dump_data(data, indent=''):
    return '\n%s' % ('\n'.join(
        ('%s%s: %s' % (indent, _tag(k), dump_data(v, indent + '\t') if isinstance(v, DynamicObject) else v) for k, v in
         data.to_dict().items())))


def match(text, lexer_list, context):
    """Cut out first matched string by multiple lexers
    return the match result and the remain text
    """

    for lexer in lexer_list:
        flags = lexer.flags if lexer.flags else 0
        lexer_match = re.match(lexer.rule, text, flags)
        if lexer_match:
            # Get the counter tag
            tag = lexer.tag
            if lexer.condition:
                condition_flag, condition_tag = lexer.condition
                if get_data(context, condition_flag):
                    tag = condition_tag

            # Get the match result
            match_result = lexer_match.group()
            match_count = match_result.count('\n')

            # Recognize space lines among a multi-line comment
            if tag == config.LEX_COMMENT:
                space_all = re.findall(r'(?<=\n)\s*?\n', match_result)
                space_count = len(space_all) if space_all else 0
                add_data(context, config.LEX_SPACE, space_count)
                match_count -= space_count

            # Check line ending
            ending_match = re.match(r'\s*?\n', text[len(match_result):], re.S)
            if ending_match:
                ending_str = ending_match.group()
                match_result += ending_str
                match_count += ending_str.count('\n')

                # Recognize a code line ending with a comment as a code line,
                #   and clear the unfinished code line flag
                if get_data(context, config.FLAG_CODE):
                    add_data(context, config.LEX_CODE, 1)
                    remove_data(context, config.FLAG_CODE)
                    match_count -= 1

            # Mark the unfinished code line
            elif tag == config.LEX_CODE:
                add_data(context, config.FLAG_CODE, 1)

            # Update the counter value
            add_data(context, tag, match_count)
            logger.debug('[%s]: %s' % (tag, match_result))

            # Update the stack status
            if lexer.stack:
                update_flag, update_count = lexer.stack
                add_data(context, update_flag, update_count, True)

            return match_result

    return None


def count_text(text, lexer_list):
    """Count a string of text"""

    # Append a '\n' at the end
    text += '\n'

    # Match lexer list
    remain = text
    match_result = True
    context = DynamicObject()
    while match_result and remain:
        match_result = match(remain, lexer_list, context)
        if match_result:
            remain = remain[len(match_result):]

    # Check remain text
    if remain:
        logger.debug('Remain: <<<%s>>>' % remain)

    # Check text line count
    local_line_count = reduce(lambda a, b: a + b, context.to_dict().values(), 0)
    text_line_count = text.count('\n')
    if local_line_count != text_line_count:
        logger.debug('Text Line Count: %d, Matched Line Count: %d' % (text_line_count, local_line_count))

    if not get_data(context, config.LEX_TOTAL):
        add_data(context, config.LEX_TOTAL, text_line_count, False)

    return context


def count_file(file_path, data):
    """Count a file"""

    # Filter the file path
    path = file_path.replace('\\', '/')
    for i_rule in config.IGNORED_FILES:
        if re.match(i_rule, path):
            return

    # Read file content
    file_in = open(path, 'r')
    text = file_in.read()
    file_in.close()

    # Count the file text
    for f_handler in config.FILE_HANDLER_LIST:
        # Skip irrelevant files
        if not re.match(f_handler.path, path.lower()):
            continue

        # count line numbers
        text_context = count_text(text, f_handler.lexer_list)
        logger.info('%s -> %s' % (path, get_data(text_context, config.LEX_TOTAL, 0)))

        # Check count result
        keys = set(map(_tag, text_context.to_dict().keys()))
        if keys - config.LEX_LIST:
            count_result = dump_data(text_context, '\t')
            logger.error('[Error] path={%s}, tag={%s}, data={%s}' % (path, f_handler.tag, count_result))
            exit()

        """ Add up text data to file data, all data,
            and optionally the test data.
        """
        tag_list = [f_handler.tag, config.TAG_ALL]
        if re.match(r'.*?/test/', path):
            tag_list.append(config.TAG_TEST)

        data_list = [update_data(data, tag, DynamicObject()) for tag in tag_list]
        for key, line_count in text_context.to_dict().items():
            [add_data(_data, _tag(key), line_count) for _data in data_list]

        # Skip other file handlers
        return


def count(path):
    """Count a path"""

    class _Handler(WalkHandler):
        def handle_file(self, file_path, context):
            count_file(file_path, context.data)

        def handle_dir_pre(self, dir_path, context):
            context.short_circuit = os.path.basename(dir_path) in config.IGNORED_FOLDERS

        def check_short_circuit(self, _, context):
            short_circuit = context.short_circuit
            context.short_circuit = False
            return short_circuit

    walk_context = DynamicObject()
    walk_context.data = DynamicObject()
    walk_context.short_circuit = False

    all_data = DynamicObject()
    update_data(all_data, config.LEX_TOTAL, 0)
    update_data(walk_context.data, config.TAG_ALL, all_data)

    walk(path, _Handler(), context=walk_context)
    logger.debug(dump_data(walk_context.data))

    return walk_context.data
