#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 16:29:00 2019

@author: Paolo Cozzi <cozzi@ibba.cnr.it>
"""

import os
import sys
import json
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

    def __init__(self, filename, size):
        self._filename = filename
        self._size = size
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


def dump_data(data):
    json.dump(
        data,
        sys.stdout,
        indent=2,
        sort_keys=True,
        default=str)


def parse_args():
    parser = argparse.ArgumentParser(
        description=('Upload data into digitalocean space')
    )

    parser.add_argument(
        "-i",
        "--input_dir",
        help="Input directory to download",
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

    # test for directory existance
    if not os.path.exists(args.input_dir):
        logger.info("Creating %s" % (args.input_dir))
        os.mkdir(args.input_dir)

    session = boto3.session.Session()

    logger.info("connect to digitalocean endpoint")

    client = session.client(
        args.service_name,
        region_name=args.region_name,
        endpoint_url='https://{region}.digitaloceanspaces.com/'.format(
            region=args.region_name),
        aws_access_key_id=args.space_key_name,
        aws_secret_access_key=args.space_key_secret)

    # get bucket data
    data = client.list_objects(Bucket=args.bucket)

    # dump object
    # dump_data(data)

    for file_object in data["Contents"]:
        # get the key (path)
        path = file_object["Key"]
        size = file_object["Size"]

        # test for file existance
        if os.path.exists(path):
            logger.warning("Skipping %s" % (path))
            continue

        # split key and test for input_dir
        if path.split("/")[0] == args.input_dir:
            client.download_file(
                Bucket=args.bucket,
                Filename=path,
                Key=path,
                Callback=ProgressPercentage(path, size))

    # debug
    logger.info("Done!")
