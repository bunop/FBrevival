#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 11:51:07 2018

@author: Paolo Cozzi <cozzi@ibba.cnr.it>
"""

import os
import sys
import boto3
import logging
import threading

from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

# set values
GB = 1024 ** 3


class ProgressPercentage(object):
    """A callback to see progress percentage"""

    def __init__(self, filename):
        self._filename = filename
        self._size = int(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

            if self._seen_so_far >= self._size:
                sys.stdout.write("\n")
                sys.stdout.flush()


def exists(client, bucket, key):
    try:
        client.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


# Ensure that multipart uploads only happen if the size of a transfer
# is larger than S3's size limit for nonmultipart uploads, which is 5 GB.
# Decrease the max concurrency from 10 to 5 to potentially consume
# less downstream bandwidth.
config = TransferConfig(multipart_threshold=1 * GB, max_concurrency=5)

# upload directory as argument
mydir = sys.argv[1]

# the space in question
bucket = "exchange1"

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

logger.info("Got %s as directory" % mydir)

session = boto3.session.Session()

logger.info("connect to digitalocean endpoint")

client = session.client(
    's3',
    region_name='ams3',
    endpoint_url='https://ams3.digitaloceanspaces.com/',
    aws_access_key_id='***REMOVED***',
    aws_secret_access_key='***REMOVED***')

# list buckets
# print(client.list_buckets())

for myfile in os.listdir(mydir):
    path = os.path.join(mydir, myfile)

    if os.path.isdir(path):
        logger.warning("Skipping %s: is a directory" % (path))
        continue

    if exists(client, bucket, path):
        logger.warning("Skipping %s: already uploaded" % (path))
        continue

    logger.info("Loading '%s' into '%s' space" % (path, bucket))

    # upload a file
    client.upload_file(
        Bucket=bucket,
        Filename=path,
        Key=path,
        Callback=ProgressPercentage(path))

    # debug
    # break

# list file
# print(client.list_objects(Bucket='excange'))

# debug
logger.info("Done!")
