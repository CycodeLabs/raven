#!/bin/bash

# Global variable to store the tarball URL
tarball_url=""
raven_tar="raven.tar.gz"
tag_name=""
short_commit_hash=""

# Handle errors and exit the script with an error message
handle_error() {
  echo "Error: $1"
  exit 1
}

# Get the latest release from GitHub
get_latest_release() {
  local release_url="https://api.github.com/repos/CycodeLabs/raven/releases/latest"

  res=$( curl -sSfL "$release_url" )
  tarball_url=$( echo $res | jq -r '.tarball_url' )
  tag_name=$( echo $res | jq -r '.tag_name' )


  if [ -z "$tarball_url" ]; then
    handle_error "Failed to extract tarball_url from the latest release"
  fi
}

# Download the latest release tarball
download_tarball() {
  wget -O $raven_tar -L "$tarball_url" || handle_error "Failed to download the tarball with wget"
}

get_commit_hash() {
  local tag_url="https://api.github.com/repos/CycodeLabs/raven/git/refs/tags/$tag_name"

  res=$( curl -sSfL "$tag_url" )
  local commit_hash=$( echo $res | jq -r '.object.sha' )
  short_commit_hash="${commit_hash:0:7}"

  if [ -z "$short_commit_hash" ]; then
    handle_error "Failed to commit hash"
  fi

}

get_latest_release
download_tarball
get_commit_hash

tar -xf $raven_tar
mv "CycodeLabs-raven-$short_commit_hash" raven