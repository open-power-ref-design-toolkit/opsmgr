#!/bin/bash
pushd `dirname $0`
echo -ne '{ "osa_inventory": ' > ../ext/osa_inv.json
cat /tmp/osa_inv.json >> ../ext/osa_inv.json
echo ' }' >> ../ext/osa_inv.json
rm -f /tmp/osa_inv.json
popd
