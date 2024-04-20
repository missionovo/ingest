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
from pathlib import Path
import socket
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
    hostname = socket.gethostname()
    datestr = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_key = f"{customer}/{hostname}/{type}{datestr}.log"

    print(f"loading object with key: {file_key} at bucket: {bucket}; body length: {len(entries)}")

    s3_object = s3.Object(Bucket=bucket, Key=file_key)
    s3_object.put(Body='\n'.join(entries))

def main(
        log_path: str
    ):
  assert Path(log_path).is_file(), ('"%s" is not a file or is missing' % log_path)
  #print(f"this is the path we are using: {log_path}")
  file_id = unique_file_identifier(log_path)

  line_group = []
  f = open(log_path, 'r')
  try:
    while True:
      line = f.readline()
      if line:
        line_group.append(line)
      else:
        # Only send the lines once we are all caught up (line = None)
        if len(line_group) > 0:
          yield line_group
          line_group = []

        # Check if the log has rotated. If so, get the new log file
        # TODO: any potential errors to handle here? missing file? etc?
        latest_file_id = unique_file_identifier(log_path)
        if latest_file_id != file_id:
          file_id = latest_file_id
          f.close()
          f = open(log_path, 'r')

        # Wait for more lines to accumulate
        time.sleep(0.5)
  finally:
    f.close()

def unique_file_identifier(filename):
  # NOTE: `st_ino` is always 0 on windows, which won't work
  return Path(filename).stat().st_ino

if __name__ == "__main__":
    parsed = args.parse_args()
    conf_path = parsed.config

    if os.path.exists(conf_path):
        config.read(conf_path)
        if parsed.type in config and "bucket" in config["default"] and "customer" in config["default"]:
            bucket=config["default"]["bucket"]
            customer=config["default"]["customer"]
            log_entries = []
            log_bytes = 0
            type=parsed.type

            for line in main(log_path=config[parsed.type]["path"].strip()):
                log_bytes += len(line)
                log_entries.append(line)

                if log_bytes >= MAX_LOG_BYTES:
                    send_to_s3(bucket=bucket,customer=customer,entries=log_entries,type=type)
                    log_bytes = 0
                    log_entries = []
        else:
            print(f'''required parameters missing from configuration file. make sure default has
                  populated keys for bucket and customer and the type {parsed.type} you are adding
                  has an entry for path.''')
