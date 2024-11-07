#!/bin/bash

# apt packages for RPD
echo "Installing dependencies for RPD..."
apt update
apt install sqlite3 libsqlite3-dev
apt install libfmt-dev
cd rocmProfileData
make; make install

cd ..
# Dependencies for Amelia
echo "
Installing dependencies for Amelia..."
pip install -r requirements.txt
pip install langchain-community