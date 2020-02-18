#!/bin/bash

set -x

echo Installing auto transfer
echo Python 3 is not installed
apt-get update  # To get the latest package lists
apt-get install python3 -y
echo Python3-dev is not installed

apt-get install python3-dev -y

echo python3-pip is not installed

apt-get install python3-pip -y

INSTALL_DIR=${HOME}/autotransfer
VPYTHON=/usr/local/bin/python3
VPIP=/usr/local/bin/pip3

mkdir -p $INSTALL_DIR
#python3 -m venv $VPYTHON_DIR
#$VPIP install -r requirements.txt

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
