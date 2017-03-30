import findspark
findspark.init()
import pyspark
import config

from google.cloud import storage
import googleapiclient.discovery

def spark_session():
    return pyspark.sql.SparkSession \
        .builder \
        .master(config.SPARK_URL) \
        .appName(config.APP_NAME) \
        .enableHiveSupport() \
        .getOrCreate()

def storage_client():
    client = storage.Client()
    bucket = client.get_bucket(config.BUCKET_NAME)
    return bucket

def dataproc_client():
    """Builds a client to the dataproc API."""
    dataproc = googleapiclient.discovery.build('dataproc', 'v1')
    return dataproc
