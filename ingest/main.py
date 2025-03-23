import logging
from pyspark.sql import SparkSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

namespace = "trendmicro"
table_name = "test_table"
full_table_name = f"rest.{namespace}.{table_name}"
parquet_directory_path = "file:///mnt/d/trendmicro-data/stg_600g_merge/x=00"

spark = (
    SparkSession.builder.appName("Parquet to Iceberg")
    .config(
        "spark.jars.packages",
        "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.8.1,"
        "software.amazon.awssdk:s3:2.26.19,"
        "software.amazon.awssdk:auth:2.26.19,"
        "software.amazon.awssdk:core:2.26.19,"
        "software.amazon.awssdk:sts:2.26.19,"
        "software.amazon.awssdk:glue:2.26.19,"
        "software.amazon.awssdk:dynamodb:2.26.19,"
        "software.amazon.awssdk:kms:2.26.19,"
    )
    .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    .config("spark.sql.defaultCatalog", "rest")
    .config("spark.sql.catalog.rest.type", "rest")
    .config("spark.sql.catalog.rest", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.rest.default-namespace", "trendmicro")
    .config("spark.sql.catalog.rest.uri", "http://127.0.0.1:8181")

    .config("spark.sql.catalog.rest.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
    .config("spark.sql.catalog.rest.warehouse", "s3a://test-bucket/trendmicro")
    .config("spark.sql.catalog.rest.s3.endpoint", "http://127.0.0.1:9000")
    .config("spark.sql.catalog.rest.s3.region", "us-east-1")
    .config("spark.sql.catalog.rest.s3.access-key-id", "admin")
    .config("spark.sql.catalog.rest.s3.secret-access-key", "password")
    .config("spark.sql.catalog.rest.s3.path-style-access", "true")

    .config("spark.hadoop.fs.s3a.access.key", "admin")
    .config("spark.hadoop.fs.s3a.secret.key", "password")
    .config("spark.hadoop.fs.s3a.endpoint", "http://127.0.0.1:9000")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.driver.extraJavaOptions", "-Daws.region=us-east-1")
    .config("spark.executor.extraJavaOptions", "-Daws.region=us-east-1")
    
    .config("spark.driver.memory", "81g")
    .config("spark.executor.memory", "81g")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("INFO")

spark.sql("CREATE NAMESPACE IF NOT EXISTS trendmicro")
df = spark.read.parquet(parquet_directory_path)
logger.info(f"Successfully read {df.count()} rows from Parquet")

# Add mode="overwrite" to force rewrite if needed
df.write.format("iceberg").mode("overwrite").partitionBy(
    "customerId", "year", "month", "day"
).saveAsTable(full_table_name)

# List files to check locations
files_df = spark.sql(f"SELECT file_path FROM {full_table_name}.files")
logger.info(f"Files in table {full_table_name}")
files_df.show(10, truncate=False)

spark.stop()