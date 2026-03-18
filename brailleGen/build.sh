#!/usr/bin/env bash

apt-get update
apt-get install -y liblouis-dev liblouis-data

pip install -r requirements.txt