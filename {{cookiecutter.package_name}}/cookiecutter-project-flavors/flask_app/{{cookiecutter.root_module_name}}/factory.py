"""
{{cookiecutter.root_module_name}}.factory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Factory for instances of the Flask application

"""

#
# Imports
#

# core python
import logging
import os

# third party
import flask

# this project
import {{ cookiecutter.root_module_name }}.blueprints.core as my_core_blueprint

#
# Module variables
#

# os env var for config overrides etc.
FLASK_CONFIG_PATH_ENV_VAR = "{{ cookiecutter.project_name | upper | replace(' ', '_') }}_FLASK_CONFIG_PATH"

# logging
_LOGGER = logging.getLogger(__name__)


#
# Helper functions
#

def _load_app_config(flask_app):
    """Load the config for the flask application"""
    _LOGGER.info("Begin loading flask app config settings")
    assert flask_app is not None

    if os.getenv(FLASK_CONFIG_PATH_ENV_VAR, None) is not None:
        _LOGGER.info("Reading config settings from path in ENV variable %s",
                     FLASK_CONFIG_PATH_ENV_VAR)
        flask_app.config.from_envvar(FLASK_CONFIG_PATH_ENV_VAR)
    else:
        _LOGGER.info("Using default settings since env variable %s is not set",
                     FLASK_CONFIG_PATH_ENV_VAR)
        default_settings = {
            # toggle debug and testing on
            'DEBUG': True,
            'TESTING': True,
            # JSON settings for easier debugging
            'JSON_AS_ASCII': False,
            'JSON_SORT_KEYS': True,
            'JSONIFY_PRETTYPRINT_REGULAR': True,
            # Placeholder for 'real' security stuff
            'SECRET_KEY': 'super-secret-key',
            # pylint: disable=fixme
            # TODO - Put other sane defaults here as well
        }
        _LOGGER.debug("Using default settings: %s", default_settings)
        flask_app.config.from_mapping(default_settings)
    _LOGGER.info("Finished loading flask app config settings")


#
# Factory function
#

def build_app():
    """Builds a Flask application instance"""
    _LOGGER.info("Begin building an instance of a Flask application object")
    # setup basic app object
    app = flask.Flask(__name__, instance_relative_config=True)

    # load config settings into it
    _load_app_config(app)

    # do final configuration of any extensions
    # pylint: disable=fixme
    # TODO - None in this skeleton, but you'd import their objects and call `init_app` with them
    # Example:
    #     {{cookiecutter.root_module_name}}.extensions.my_extension.MY_SINGLETON.init_app(app)
    #

    # register blueprints
    app.register_blueprint(my_core_blueprint.BP)

    # return it
    _LOGGER.info("Finished building an instance of a Flask application object")
    return app
