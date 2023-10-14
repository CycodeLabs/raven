#!/bin/bash

# Global variable to store the tarball URL
tarball_url=""

# Handle errors and exit the script with an error message
handle_error() {
  echo "Error: $1"
  exit 1
}

# Get the latest release from GitHub
get_latest_release() {
  local release_url="https://api.github.com/repos/CycodeLabs/raven/releases/latest"

  tarball_url=$(curl -s "$release_url" | jq -r '.tarball_url')

  if [ -z "$tarball_url" ]; then
    handle_error "Failed to extract tarball_url from the latest release"
  fi
}

# Download the latest release tarball
download_tarball() {
  wget -O raven.tar.gz -L "$tarball_url" || handle_error "Failed to download the tarball with wget"
}

get_latest_release
download_tarball

tar -xvf raven.tar.gz --one-top-level=raven
cd raven