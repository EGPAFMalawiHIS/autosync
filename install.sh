#!/bin/bash

echo Installing auto transfer

if command -v python3 &>/dev/null; then
    echo Python 3 is installed
else
    echo Python 3 is not installed
    apt-get update  # To get the latest package lists
	apt-get install python3 -y
fi


if command -v python3-dev &>/dev/null; then
    echo Python3-dev is installed
else
    echo Python3-dev is not installed
    
	apt-get install python3-dev -y
fi

if command -v python3-pip &>/dev/null; then
    echo python3-pip is installed
else
    echo python3-pip is not installed
    
	apt-get install python3-pip -y
fi

if command -v python3-venv &>/dev/null; then
    echo python3-venv is installed
else
    echo python3-venv is not installed
    
	apt-get install python3-venv -y
fi


mkdir -p ~/autotransfer

cd ~/autotransfer

#python3 -m venv .autoenv

#source .autoenv/bin/activate

pip3 install cryptography
#pip3 install json
#pip3 install socket

#deactivate

cd ~/

mv autotransferb.service /etc/systemd/system/autotransfer.service
mv site.txt /home/user/autotransfer
mv sms_send.py /home/user/autotransfer

sudo systemctl start autotransfer

sudo systemctl enable autotransfer

echo Service Succesfully Installed 









