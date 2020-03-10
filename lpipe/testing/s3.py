import backoff
import boto3
from botocore.exceptions import ClientError, ConnectionClosedError

from .. import utils


@backoff.on_exception(backoff.expo, (ClientError, ConnectionClosedError), max_time=30)
def create_s3_bucket(b: str):
    client = boto3.client("s3")
    resp = utils.call(client.create_bucket, Bucket=b)
    client.get_waiter("bucket_exists").wait(Bucket=b)
    return resp


def create_s3_buckets(names: list):
    return {n: create_s3_bucket(n) for n in names}


@backoff.on_exception(backoff.expo, (ClientError, ConnectionClosedError), max_time=30)
def destroy_s3_bucket(b: str):
    client = boto3.client("s3")
    objects = boto3.resource("s3").Bucket(b).objects.all()
    keys = [utils.call(client.delete_object, Bucket=b, Key=o.key) for o in objects]
    resp = utils.call(client.delete_bucket, Bucket=b)
    client.get_waiter("bucket_not_exists").wait(Bucket=b)
    return resp


def destroy_s3_buckets(names: list):
    return {n: destroy_s3_bucket(n) for n in names}