#! /bin/bash
#set -x

NICK=$1
NAME=$(/usr/bin/sudo /usr/bin/lxc-ls | grep $NICK)
shift
FILE=$1
shift
RARGS=$@

cp /etc/nagios/plugins/$FILE /var/lib/lxc/$NAME/rootfs/tmp

EXECFILE=/tmp/$FILE
if [[ $NICK == "utility" ]]; then
    RCMD=". /root/openrc; $EXECFILE $RARGS"
else
    RCMD="$EXECFILE $RARGS"
fi

OUT=$(/usr/bin/sudo /usr/bin/lxc-attach --name $NAME -- sh -c "$RCMD")
RESULT=$?

#rm -f /var/lib/lxc/$NAME/rootfs/tmp/$FILE

echo $OUT
exit $RESULT
