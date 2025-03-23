import boto3
import os
import re

s3 = boto3.client("s3")

bucket = "jason-test-iceberg"
prefix = "stg_600g_merge/"

paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

# Matches keys like 'stg_600g_merge/x=00/part-00000-...snappy.parquet'
pattern = re.compile(r"stg_600g_merge/x=[0-9A-Fa-f]{2}/.*\.snappy\.parquet$")

for page in pages:
    print(f"length: {format(len(page.get('Contents', [])))}")
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if pattern.match(key):
            local_path = os.path.join("/mnt/d/trendmicro-iceberg-data", key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(bucket, key, local_path)
            print(f"Downloaded {key} to {local_path}")
