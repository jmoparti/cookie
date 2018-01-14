#!/usr/bin/env bash

set -e

echo "Provisioning the vm used for system testing"

#
# Parse cli args
#

python_version_name="${1}"
if [[ "${python_version_name}" == "py27" ]]; then
    python_interpreter_name="python2.7"
    uwsgi_py_env="python27"
elif [[ "${python_version_name}" == "py34" ]]; then
    python_interpreter_name="python3.4"
    uwsgi_py_env="python3"
elif [[ "${python_version_name}" == "py35" ]]; then
    python_interpreter_name="python3.5"
    uwsgi_py_env="python3"
else
    echo "ERROR: Unsupported python environment name: '${1}'"
fi


#
# Install apt-dependencies
#

# install uwsgi and python deps for it
apt-get install -y uwsgi
if [[ "${python_version_name}" == "py27" ]]; then
    apt-get install -y uwsgi-plugin-python
elif [[ "${python_version_name}" == "py34" ]]; then
    apt-get install -y uwsgi-plugin-python3
elif [[ "${python_version_name}" == "py35" ]]; then
    apt-get install -y uwsgi-plugin-python3
else
    echo "ERROR: Unsupported python environment name: '${1}'"
fi

# install nginx
apt-get install -y nginx

# install helper tools
apt-get install -y wget tree

#
# setup the home for the app
#

echo "Setting up opt dir for assets"
mkdir -p /opt/{{cookiecutter.package_name}}

echo "Creating and activating the virtualenv"
virtualenv_path=/opt/{{cookiecutter.package_name}}/venv

if [[ -e ${virtualenv_path} ]]; then
    echo "Removing existing virtualenv"
    rm -r ${virtualenv_path}
fi

virtualenv --python ${python_interpreter_name} ${virtualenv_path}
source ${virtualenv_path}/bin/activate

# upgrade pip inside the virtualenv
pip install -U pip

# install dependencies to the virtualenv
pip install -r /vagrant/requirements.txt

# install the app from its wheel to the virtualenv
whl_file_prefix="{{ cookiecutter.package_name | lower | replace('-', '_') }}"
for whl_file in $(find /vagrant/dist/ -name "${whl_file_prefix}*.whl" | sort)
do
    pip install -U ${whl_file}
done
deactivate

#
# configure uwsgi and nginx
#

echo "Shutdown uwsgi and nginx before generating custom configs"
service uwsgi stop
service nginx stop

echo "Generating config file for flask app"
cat > /opt/{{cookiecutter.package_name}}/flask.cfg << "END_BLOCK"
DEBUG=True
TESTING=True
JSON_AS_ASCII=False
JSON_SORT_KEYS=True
JSONIFY_PRETTYPRINT_REGULAR=True
SECRET_KEY='super-secret-key'
END_BLOCK

echo "Generating config file for uwsgi"
cat > /etc/uwsgi/apps-available/{{cookiecutter.package_name}}.ini << "END_BLOCK"
[uwsgi]

plugins = __UWSGI_PLUGINS__
module = {{cookiecutter.root_module_name}}.uwsgi
callable = application
master = true
processes = 4

socket = /var/lib/nginx/uwsgi/{{cookiecutter.package_name}}.sock
chmod-socket = 660
vacuum = true

die-on-term = true
plugins=python
uid = www-data
gid = www-data
env = {{ cookiecutter.project_name | upper | replace(' ', '_') }}_FLASK_CONFIG_PATH=/opt/{{cookiecutter.package_name}}/flask.cfg
virtualenv=/opt/{{cookiecutter.package_name}}/venv
END_BLOCK

# replace the __UWSGI_PLUGINS__ placeholder with real value
sed -i "s/__UWSGI_PLUGINS__/${uwsgi_py_env}/" /etc/uwsgi/apps-available/{{cookiecutter.package_name}}.ini

# activate new app
ln -s /etc/uwsgi/apps-available/{{cookiecutter.package_name}}.ini /etc/uwsgi/apps-enabled/{{cookiecutter.package_name}}.ini

echo "Generating config file for nginx"
cat > /etc/nginx/sites-available/{{cookiecutter.package_name}}.conf << "END_BLOCK"

# Regular port 80 server.  We will keep this until everything is switched to SSL.
server {
    listen 80 default_server;
    listen [::]:80 default_server ipv6only=on;
    root       /usr/share/nginx/html;

    location / {
        uwsgi_pass unix:/var/lib/nginx/uwsgi/{{cookiecutter.package_name}}.sock;
        include uwsgi_params;
    }
}
END_BLOCK

# deactivate default nginx site
rm /etc/nginx/sites-enabled/default

# activate new custom site
ln -s /etc/nginx/sites-available/{{cookiecutter.package_name}}.conf /etc/nginx/sites-enabled/{{cookiecutter.package_name}}.conf

#
# Restart nginx and uwsgi with new configs
#

echo "Start uwsgi and nginx with custom configs"
service uwsgi start
service nginx start

echo "Sleep for a second to let things warm up"
sleep 1

echo "Hit the nginx url to see if things are up"
wget http://localhost:80 --output-document -

echo "Done!"
