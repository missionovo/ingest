#!/bin/bash
if [ -z "$1" ]; then
    echo 'specify customer name as first arg to this script'
    exit 1
fi
pushd $(dirname $0)
curl https://raw.githubusercontent.com/fluent/fluent-bit/master/install.sh | sh
cp fluent-bit.conf /etc/fluent-bit/fluent-bit.conf
cp auditd.rules /etc/audit/rules.d/auditd.rules
echo "CUSTOMER=$1" > /etc/sysconfig/fluent-bit
systemctl restart fluent-bit
popd