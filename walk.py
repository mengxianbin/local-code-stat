import os


class WalkHandler(object):
    def gen_default_context(self):
        """Generate a default context"""
        pass

    def handle_file(self, path, context):
        pass

    def handle_dir_pre(self, path, context):
        """Do something before handle a directory"""
        pass

    def handle_dir_post(self, path, context):
        """Do something after handle a directory"""
        pass

    def check_short_circuit(self, path, context):
        """Check whether the walk could short-circuit the directory traversal.
        This method will be invoked before handling a file or a directory.
        """
        pass


def walk(path, handler, context=None):
    """Walk a path recursively to call your handler"""

    # Check the context
    context = context if context else handler.gen_default_context()

    # Ensure the path format
    path = path.replace('\\', '/')

    # Check short circuit
    if handler.check_short_circuit(path, context):
        return

    # Handle the file
    if os.path.isfile(path):
        handler.handle_file(path, context)

        # Finish the file handle
        return

    # Do handle before traverse
    handler.handle_dir_pre(path, context)

    # Walk path recursively
    for sub_name in os.listdir(path):

        # Check short circuit
        if handler.check_short_circuit(path, context):
            break

        # Walk each sub-directory or file
        sub_path = os.path.join(path, sub_name)
        walk(path=sub_path, handler=handler, context=context)

    # Do handle after traverse
    handler.handle_dir_post(path, context)
