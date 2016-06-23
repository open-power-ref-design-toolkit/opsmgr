#!/bin/bash
pushd `dirname $0`
echo -ne '{ "osa_inventory": ' > ../etc/osa_inv.json
cat /tmp/osa_inv.json >> ../etc/osa_inv.json
echo ' }' >> ../etc/osa_inv.json
rm -f /tmp/osa_inv.json
popd
