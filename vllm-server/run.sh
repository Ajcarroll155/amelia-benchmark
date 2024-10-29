#!/bin/bash

[[ -z "$DEBUG" ]] && ARGS="-d" || ARGS="" echo "INFO: Running in debug mode"

docker compose up $ARGS 
