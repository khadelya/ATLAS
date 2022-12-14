#!/usr/bin/env bash

set -e

currentVersion=$(git rev-parse HEAD)
baseImage="adelya/object-detection-worker"
versionTag="${baseImage}:${currentVersion}"
latesTag="${baseImage}:latest"
docker build \
	-t "${versionTag}" \
	-t "${latesTag}" \
	.

