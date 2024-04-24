#!/bin/bash
if [ -z "$1" ]; then
    echo 'specify customer name as first arg to this script'
    exit 1
fi

rm -rf ingest-fluent-bit
wget https://github.com/missionovo/ingest/archive/refs/heads/fluent-bit.zip
unzip fluent-bit.zip
rm -f fluent-bit.zip

pushd ingest-fluent-bit
curl https://raw.githubusercontent.com/fluent/fluent-bit/master/install.sh | sh
cp fluent-bit.conf /etc/fluent-bit/fluent-bit.conf
cp auditd.rules /etc/audit/rules.d/auditd.rules
service auditd restart
systemctl daemon-reload
echo "CUSTOMER=${1,,}" > /etc/sysconfig/fluent-bit
systemctl restart fluent-bit
popd

rm -rf ingest-fluent-bit