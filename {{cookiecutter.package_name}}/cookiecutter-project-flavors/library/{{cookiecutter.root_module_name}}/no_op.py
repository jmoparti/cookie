"""
{{cookiecutter.root_module_name}}.no_op
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No-op example of some functions provided by the library.
"""

#
# Imports
#

# core python
import logging

# third party

# this project
import {{ cookiecutter.root_module_name }}.exceptions as my_exceptions

#
# Module variables
#

# logging
_LOGGER = logging.getLogger(__name__)

#
# Classes/functions
#

def totally_useless_concat(some_string, some_other_string):
    """
    Concatenate two strings.

    Example of a function and docstrings.

    Arguments:
        some_string (str): The first string.  May not be None.
        some_other_string (str): The second string.  May not be None.

    Returns:
        str : The concatenated strings

    Raises:
        :py:exc:`{{cookiecutter.root_module_name}}.exceptions.GeneralException` : Raised if
              either of the input strings are None.
    """
    _LOGGER.debug("Begin totally useless activity")
    if some_string is None:
        raise my_exceptions.GeneralException("some_string was None")
    if some_other_string is None:
        raise my_exceptions.GeneralException("some_other_string was None")
    result = some_string + some_other_string
    _LOGGER.debug("Finished totally useless activity")
    return result
