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

INSTALL_DIR=${HOME}/autotransfer
VPYTHON_DIR=${INSTALL_DIR}/.autoenv
VPYTHON=${VPYTHON_DIR}/bin/python
VPIP=${VPYTHON_DIR}/bin/pip

mkdir -p $INSTALL_DIR
$VPYTHON -m venv $VPYTHON_DIR
$VPIP install -r requirements.txt

cp -Rv .env site.txt sms_send.py settings.py emr_api/ $INSTALL_DIR

cat > /etc/systemd/system/autotransfer.service <<EOF
[Unit]
Description = EGPAF Auto Data Transfer Service
After       = network.target

[Service]
WorkingDirectory=$INSTALL_DIR
ExecStart=$VPYTHON ${INSTALL_DIR}/sms_send.py &> ${INSTALL_DIR}/send_sms.log
ExecStop=/bin/kill -INT \$MAINPID
ExecReload=/bin/kill -TERM \$MAINPID

# In case if it gets stopped, restart it immediately
Restart     = always

Type        = simple


[Install]
# multi-user.target corresponds to run level 3
# roughtly meaning wanted by system start
WantedBy    = multi-user.target
EOF

sudo systemctl start autotransfer

sudo systemctl enable autotransfer

echo Service Succesfully Installed 
