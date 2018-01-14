"""
{{cookiecutter.root_module_name}}.uwsgi
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shim module for hoisting into uwsgi environment

"""

#
# Imports
#

# core python
import logging
import sys

# this project
import {{ cookiecutter.root_module_name }}.factory as my_factory

#
# Prep
#

# setup initial logging config
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)

# build the app instance and publish as module variable for uwsgi pickup
application = my_factory.build_app()

# dial logging up/down based on config
if not application.config['DEBUG']:
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
