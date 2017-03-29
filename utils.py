import findspark
findspark.init()
import pyspark

from google.cloud import storage

def sparkSession():
    return pyspark.sql.SparkSession \
        .builder \
        .appName('githubArchiveExplorer') \
        .enableHiveSupport() \
        .getOrCreate()

def dataBucket():
    client = storage.Client()
    bucket = client.get_bucket('githubarchivedata')
    return bucket
