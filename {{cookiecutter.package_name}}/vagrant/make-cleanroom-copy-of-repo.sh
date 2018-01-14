#!/usr/bin/env bash

##########################################
# Makes a "cleanroom" copy of the repo
##########################################

#
# Global config
#

# Fail faster
set -e
set -o pipefail

# get a unique id
unique_id=$$_$(date +%s)

#
# Parse command line arg(s)
#

if [[ -z "${1}" ]]; then
  echo "ERROR: Missing first argument, the origin path"
  exit 1
fi
origin_path="${1}"

if [[ -z "${2}" ]]; then
  echo "ERROR: Missing first argument, the destination path"
  exit 1
fi
destination_path="${2}"

#
# Collect the list of git-managed files
#

# setup temp directory and file
temp_path=/tmp/make-cleanroom-copy-of-repo-${unique_id}
mkdir -p ${temp_path}
rsync_files_from_file=${temp_path}/git.files

# get the git list
cd ${origin_path}
git ls-files > ${rsync_files_from_file}
echo ".git" >> ${rsync_files_from_file}

#
# Run rsync
#

rsync -av --files-from=${rsync_files_from_file} ${origin_path} ${destination_path}
