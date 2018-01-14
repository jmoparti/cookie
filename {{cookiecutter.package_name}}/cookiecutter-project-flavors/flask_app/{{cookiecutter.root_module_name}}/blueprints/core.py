"""
{{cookiecutter.root_module_name}}.blueprints.core
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Blueprint for core routes exposed by this application.

e.g. the root URL "/", etc.
"""

#
# Imports
#

# core python
import logging

# third party
import flask

# this project

#
# Module variables
#

# logging
_LOGGER = logging.getLogger(__name__)

# setup blueprint singleton
BP = flask.Blueprint('core', __name__, url_prefix="/", static_folder='static', template_folder='templates/core')

#
# Routes
#

@BP.route('/', methods=['GET'])
@BP.route('index.html', methods=['GET'])
def get_index():
    return flask.render_template('index.html')
