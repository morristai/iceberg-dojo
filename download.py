import boto3
import os
import re

# Initialize the S3 client
s3 = boto3.client("s3")

# Define the bucket and prefix
bucket = "jason-test-iceberg"
prefix = "stg_600g_merge/"

# Create a paginator to handle large numbers of objects
paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

# Regular expression to match Parquet files under x=XX/ directories
# Matches keys like 'stg_600g_merge/x=00/part-00000-...snappy.parquet'
pattern = re.compile(r"stg_600g_merge/x=[0-9A-Fa-f]{2}/.*\.snappy\.parquet$")

# Iterate through all objects and download matching files sequentially
for page in pages:
    print(f"length: {format(len(page.get('Contents', [])))}")
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if pattern.match(key):
            # Define the local path, preserving the S3 directory structure
            local_path = os.path.join("/mnt/d/trendmicro-iceberg-data", key)
            # Create the local directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            # Download the file
            s3.download_file(bucket, key, local_path)
            print(f"Downloaded {key} to {local_path}")
