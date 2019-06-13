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
import argparse
import threading

from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

# set values
GB = 1024 ** 3

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

# Ensure that multipart uploads only happen if the size of a transfer
# is larger than S3's size limit for nonmultipart uploads, which is 5 GB.
# Decrease the max concurrency from 10 to 5 to potentially consume
# less downstream bandwidth.
config = TransferConfig(multipart_threshold=1 * GB, max_concurrency=5)


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


def parse_args():
    parser = argparse.ArgumentParser(
        description=('Upload data into digitalocean space')
    )

    parser.add_argument(
        "-i",
        "--input_dir",
        help="Input directory to upload",
        required=True
    )

    parser.add_argument(
        "-b",
        "--bucket",
        help="Space Bucket in which put files",
        required=True
    )

    parser.add_argument(
        "--service_name",
        help="Service name (def '%(default)s')",
        default='s3'
    )

    parser.add_argument(
        "--region_name",
        help="Region name (def '%(default)s')",
        default='fra1'
    )

    parser.add_argument(
        "--space_key_name",
        help="space key name",
    )

    parser.add_argument(
        "--space_key_secret",
        help="space key secret",
    )

    args = parser.parse_args()

    if not args.space_key_name:
        if 'DO_SPACE_KEY_NAME' in os.environ:
            args.space_key_name = os.environ['DO_SPACE_KEY_NAME']

        else:
            raise Exception(
                "You have to pass the '--space_key_name' argument or "
                "set the DO_SPACE_KEY_NAME environment variable")

    if not args.space_key_secret:
        if 'DO_SPACE_KEY_SECRET' in os.environ:
            args.space_key_secret = os.environ['DO_SPACE_KEY_SECRET']

        else:
            raise Exception(
                "You have to pass the '--space_key_secret' argument or "
                "set the DO_SPACE_KEY_SECRET environment variable")

        return args


if __name__ == "__main__":
    args = parse_args()

    logger.info("Got %s as directory" % args.input_dir)

    session = boto3.session.Session()

    logger.info("connect to digitalocean endpoint")

    client = session.client(
        args.service_name,
        region_name=args.region_name,
        endpoint_url='https://{region}.digitaloceanspaces.com/'.format(
            region=args.region_name),
        aws_access_key_id=args.space_key_name,
        aws_secret_access_key=args.space_key_secret)

    for myfile in os.listdir(args.input_dir):
        path = os.path.join(args.input_dir, myfile)

        if os.path.isdir(path):
            logger.warning("Skipping %s: is a directory" % (path))
            continue

        if exists(client, args.bucket, path):
            logger.warning("Skipping %s: already uploaded" % (path))
            continue

        logger.info("Loading '%s' into '%s' space" % (path, args.bucket))

        # upload a file
        client.upload_file(
            Bucket=args.bucket,
            Filename=path,
            Key=path,
            Callback=ProgressPercentage(path))

        # debug
        # break

    # list file
    # print(client.list_objects(Bucket='excange'))

    # debug
    logger.info("Done!")
