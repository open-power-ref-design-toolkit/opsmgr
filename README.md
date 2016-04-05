# Instructions for installing the Opsmgr Inventory code

These instructions are written for Ubuntu, however the same steps would work for other Linux Operating Systems using the correct commands for the OS. (for instance yum instead of apt-get)

python 2.7 and python 3.4, 3.5 are supported. The instructions below are for python 3.X, to use python 2.7 replace python3 with python, pip3 with pip.

## If using python 2.7 install python-dev with the command:
**sudo apt-get install python-dev**

## Install pip:
**sudo apt-get install python3-pip**


## Database:
You'll need a SQL based database supported by SQLAlchemy. The only tested database server is mysql. If you already have mysql installed, you would just need to create a database for opsmgr.

Steps to install mysql and create the database:

**sudo apt-get install mysql-server** # It will prompt for a password - remember the password used.

**sudo service mysql restart**

**mysql -u root -p**   # login with password used.

mysql>**create database opsmgr;**   # Any database name can be used - remember it for later.

mysql>**ctrl-D**

**sudo pip3 install pymysql**



## Git:
**sudo apt-get install git**

You must have an SSH key uploaded to your profile: https://gitlabhost.rtp.raleigh.ibm.com/profile/keys

See the help on creating an SSH key:
https://gitlabhost.rtp.raleigh.ibm.com/help/ssh/README

Then configure your system to use that key to access gitlabhost.rtp.raleigh.ibm.com

That can be done by creating the file **~/.ssh/config** with the contents:

`Host gitlabhost.rtp.raleigh.ibm.com
RSAAuthentication yes
IdentityFile <absolute path to your private key>`

**chmod 600 \<absolute path to your private key\>** # to fix any permission problems on the file


## Install Opsmgr Inventory
**cd ~**

**git clone git@gitlabhost.rtp.raleigh.ibm.com:Ulysses/opsmgr.git**

**cd opsmgr**

**sudo python3 setup.py install**

**cd ~/opsmgr/plugins/devices/**

for each device plugin you wish to install:

**cd \<device plugin\>**

**sudo python3 setup.py install**

## Note at this time there are no hook plugins
**cd ~/opsmgr/plugins/hooks/**

for each hook plugin you wish to install:

**cd \<hook plugin\>**

**sudo python3 setup.py install**



Run post_install_config to setup the files in /etc/opsmgr and /var/log/opsmgr. If parameters are not specified on the command line, the script will prompt for the values.

**sudo opsmgr-admin post_install_config --db_name \<database name i.e opsmgr\> --db_user \<database userid\> --db_password \<password used for db\>**

To give others authority to use the command line (read the database password)

**sudo chmod 644 /etc/opsmgr/opsmgr.conf**

Run:

**opsmgr list_supported_device_types**

to verify the expected device plugins have been installed and found


## This completes the install setups.

## To refresh your code with the latest changes from git:
**cd ~/opsmgr**

**git pull**

**sudo python3 setup.py install**

[you would also need to run **sudo python3 setup.py** install from the directory of any plugins containing updates]