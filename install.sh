#!/bin/bash

# Global variable to store the tarball URL
tarball_url=""
raven_tar="raven.tar.gz"

# Handle errors and exit the script with an error message
handle_error() {
  echo "Error: $1"
  exit 1
}

# Get the latest release from GitHub
get_latest_release() {
  local release_url="https://api.github.com/repos/CycodeLabs/raven/releases/latest"

  tarball_url=$(curl -sSfL "$release_url" | jq -r '.tarball_url')

  if [ -z "$tarball_url" ]; then
    handle_error "Failed to extract tarball_url from the latest release"
  fi
}

# Download the latest release tarball
download_tarball() {
  wget -O $raven_tar -L "$tarball_url" || handle_error "Failed to download the tarball with wget"
}

get_latest_release
download_tarball

tar -xvf $raven_tar
cd raven-$(echo $tarball_url | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | tail -1 )