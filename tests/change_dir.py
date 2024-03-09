import os
from contextlib import contextmanager


@contextmanager
def change_dir(destination):
    """
    Change the current working directory to the specified path,
    yield control, and then change back to the previous directory.

    Args:
    - destination (str): The path to change the current working directory to.
    """
    try:
        # Store the current directory
        prev_dir = os.getcwd()
        # Change to the new directory
        os.chdir(destination)
        yield
    finally:
        # Change back to the previous directory
        os.chdir(prev_dir)
