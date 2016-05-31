#! /bin/bash
#set -x

NAME=$(/usr/bin/sudo /usr/bin/lxc-ls | grep $1)
shift
FILE=$1
shift
RCMD=$@

cp /etc/nagios/opsmgr/$FILE /var/lib/lxc/$NAME/rootfs/tmp

OUT=$(/usr/bin/sudo /usr/bin/lxc-attach --name $NAME -- /tmp/$FILE $RCMD)
RESULT=$?

rm -f /var/lib/lxc/$NAME/rootfs/tmp/$FILE

echo $OUT
exit $RESULT
