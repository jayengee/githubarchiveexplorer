import findspark
findspark.init()
import pyspark

def sparkSession():
    return pyspark.sql.SparkSession \
        .builder \
        .appName('githubArchiveExplorer') \
        .enableHiveSupport() \
        .getOrCreate()
