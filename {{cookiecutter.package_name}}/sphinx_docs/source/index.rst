#################################################
{{cookiecutter.project_name}} - Version |version|
#################################################

{{cookiecutter.project_short_description}}

.. toctree::
    :maxdepth: 2

    description_shim
    usage
{%- if cookiecutter.project_flavor == 'library' %}
    api_docs
{%- endif %}
    contributing_shim
    license_shim
    todo
