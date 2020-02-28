from dynamic_object import DynamicObject
from walk import walk, WalkHandler


def test_context():
    class _Handler(WalkHandler):
        def handle_dir_pre(self, path, context):
            context.count = context.count + 1 if context.count else 1
            print('%d: %s' % (context.count, path))

    walk('..', _Handler(), DynamicObject())


if __name__ == '__main__':
    test_context()
