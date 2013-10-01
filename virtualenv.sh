#!/bin/bash

sudo mkdir ../ve
sudo chown $USER:$USER ../ve
virtualenv ../ve

. ../ve/bin/activate

easy_install -U distribute

pip install -I -r requirements.txt