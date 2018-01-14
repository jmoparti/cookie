#!/usr/bin/env bash

set -e

echo "Making an archive file containing the html docs emitted from sphinx"

package_name="{{cookiecutter.package_name}}"
version=$(cat VERSION)

archive_root_dir_name="${package_name}-${version}-html-docs"
archive_file_name="${archive_root_dir_name}.tgz"
sphinx_html_build_path="./sphinx_docs/build/html"
proj_build_path="./build"
archive_build_path="${proj_build_path}/${archive_root_dir_name}"
proj_dist_path="./dist"
archive_path="${proj_dist_path}/${archive_file_name}"

echo "Checking for dist directory"
if [[ -e ${proj_dist_path} ]]; then
  echo "Using existing dist directory"
else
  echo "Making dist directory"
  mkdir ${proj_dist_path}
fi

echo "Marshalling html docs"
if [[ -e ${archive_build_path} ]]; then
  echo "Removing existing build dir for archive"
  rm -r ${archive_build_path}
fi
mkdir -p ${archive_build_path}
cp -r ${sphinx_html_build_path}/* "${proj_build_path}/${archive_root_dir_name}"

echo "Creating tgz archive"
if [[ -e ${archive_path} ]]; then
  echo "Removing existing archive file"
  rm ${archive_path}
fi

tar -cz -f ${archive_path} -C ${proj_build_path} ${archive_root_dir_name}

echo "Successfully built html docs archive here: ${archive_path}"
