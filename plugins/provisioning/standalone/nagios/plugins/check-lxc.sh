#! /bin/bash
#set -x

NICK=$1
NAMEX=$(/usr/bin/sudo /usr/bin/lxc-ls -1 --filter=".*${NICK}.*")
NAME="$(echo -e "${NAMEX}" | sed -e 's/[[:space:]]*$//')"
shift
FILE=$1
shift
RARGS=$@

if [[ -d /var/lib/lxc/$NAME/delta0/tmp ]]; then
        cp /etc/nagios/plugins/$FILE /var/lib/lxc/$NAME/delta0/tmp
        if [[ $NICK == "swift_proxy" ]]; then
           cp /etc/nagios/plugins/swift_commands.py /var/lib/lxc/$NAME/delta0/tmp
        fi
elif [[ -d /var/lib/lxc/$NAME/rootfs/tmp ]]; then
        cp /etc/nagios/plugins/$FILE /var/lib/lxc/$NAME/rootfs/tmp
        if [[ $NICK == "swift_proxy" ]]; then
           cp /etc/nagios/plugins/swift_commands.py /var/lib/lxc/$NAME/rootfs/tmp
        fi
else
        echo "check-lxc.sh - Unable to locate the filesystem for the container $NAME on the host."
        exit 3
fi

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
