import config
import json
import pyspark

def spark_session():
    return pyspark.sql.SparkSession \
        .builder \
        .appName(config.APP_NAME) \
        .enableHiveSupport() \
        .getOrCreate()

def parse_events():
    """
    Reads all json.gz files into one RDD, subsets into
    smaller RDDs based on rules for different types of events, and ultimately
    returns a RDD of the union of them
    """

    def read_files():
        """
        Reads all json.gz files from 2011 to 2016 and unions them. Filters by
        repository language (since this was available at this point in the
        schema), then returns the resuting RDD
        """
        spark = spark_session()
        #years = ['2011', '2012', '2013', '2014', '2015', '2016']
        years = ['2015', '2016']
        data = spark.read.json('{}{}-*'.format(config.BUCKET_LOCATION, years[0]))
        for year_index in range(1, len(years)):
            data = data.union(spark.read.json('{}{}-*'.format(config.BUCKET_LOCATION, years[year_index])))

        return data

    def parse_pull_requests():
        """
        Reads from larger data RDD and returns subset of events that match the
        criteria for appropraite PullRequestEvents
        """
        pull_requests = data.filter(data.type == 'PullRequestEvent')
        pull_requests = pull_requests.filter(pull_requests.payload.pull_request.base.repo.language == 'JavaScript')
        return pull_requests

    data = read_files()

    return parse_pull_requests()

def calc_stats():
    """
    Determine n_events and n_actors
    """
    spark = spark_session()
    stats = spark.sql("""
        SELECT
            repo.id as repo_id,
            repo.name as repo_name,
            COUNT(*) as n_events,
            SUM(payload.pull_request.additions) as n_additions,
            SUM(payload.pull_request.deletions) as n_deletions,
            SUM(payload.pull_request.additions) + SUM(payload.pull_request.deletions) as edit_size,
            COUNT(DISTINCT actor) as n_actors
        FROM repo_aggregates
        GROUP BY repo
    """)
    return stats

def get():
    """
    Wrapper function to construct stat RDDs
    """
    events = parse_events()
    events.registerTempTable('repo_aggregates')
    stats = calc_stats()

    return stats
