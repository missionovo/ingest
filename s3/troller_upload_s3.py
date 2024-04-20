#!/usr/bin/python3
'''
Created By: Brett
Updated By: Brett
Created On: 2024-04-19
Updated On: 2024-04-19
Purpose: troller_upload_s3.py is a utility script to tail log files and route them to s3 for ingest into the Troller platform
'''

from argparse import ArgumentParser
import boto3
from configparser import ConfigParser
from datetime import datetime
import os
import subprocess
import select
import sys
import time
from typing import List

args = ArgumentParser(
    prog='Troller S3 Transfer',
    usage='Takes STC Logs and does a copy to S3 without truncating the file',
    description='Application takes OS logs and moves them into an S3 bucket for transfer to the Troller project'
)
args.add_argument('-c', '--config', type=str, required=True, help='path to the config file for the application')
args.add_argument('-t', '--type', type=str, required=True, help='what log type are we collecting - should tie to a stanza in troller-s3.conf')

MAX_LOG_BYTES = 1048576

config = ConfigParser()
s3 = boto3.resource("s3")

def send_to_s3(
        bucket: str,
        customer: str,
        entries: List[str],
        type: str
    ) -> None:
    datestr = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_key = f"{customer}/{type}{datestr}.txt"

    print(f"loading object with key: {file_key} at bucket: {bucket}; body length: {len(entries)}")

    s3_object = s3.Object(Bucket=bucket, Key=file_key)
    s3_object.put(Body='\n'.join(entries))

def main(
        bucket: str,
        customer: str,
        log_path: str,
        type: str
    ) -> None:

    try:
        f = subprocess.Popen(['tail', '-F', log_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)

        log_entries = []
        log_bytes = 0
        while True:
            if p.poll(2):
                line_counter = 0
                for line in f.stdout.readlines():
                    line_counter += 1
                    log_bytes += len(line)
                    log_entries.append(line)
                print(f"adding {line_counter} lines to log entries list")
            if log_bytes >= MAX_LOG_BYTES:
                send_to_s3(bucket=bucket,customer=customer,entries=log_entries,type=type)
                log_bytes = 0
                log_entries = []
            else:
                time.sleep(2)
    except Exception as e:
        print(f"An error occurred trying to iterate through the log entries: {e}")
    finally:
            print("unregistering file tail before exit")
            p.unregister(f.stdout)
            sys.exit(0)

if __name__ == "__main__":
    parsed = args.parse_args()
    conf_path = parsed.config

    if os.path.exists(conf_path):
        config.read(conf_path)
        if parsed.type in config and "bucket" in config["default"] and "customer" in config["default"]:
            main(
                bucket=config["default"]["bucket"],
                customer=config["default"]["customer"],
                log_path=config[parsed.type]["path"].strip(),
                type=parsed.type
            )
        else:
            print(f'''required parameters missing from configuration file. make sure default has
                  populated keys for bucket and customer and the type {parsed.type} you are adding
                  has an entry for path.''')
