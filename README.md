# description
- using fluent-bit to capture machine logs and send them to s3

# quickstart
```
rm -rf ingest-fluent-bit
CUSTOMER_NAME="MISSIONOVO"
wget https://github.com/missionovo/ingest/archive/refs/heads/fluent-bit.zip
unzip fluent-bit.zip
rm -f fluent-bit.zip
chmod +x ingest-fluent-bit/install.sh
sudo ./ingest-fluent-bit/install.sh $CUSTOMER_NAME
```

# customize
- feel free to customize the fluent-bit.conf file based on [this documentation](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit/classic-mode/configuration-file)
