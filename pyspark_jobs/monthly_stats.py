import config
from datetime import date, timedelta
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

        def generate_date_range(start, end):
            """
            For a given pair of start and end date objects, returns list of strings
            matching the year, month, day, hour format used by GitHub Archive
            """
            def perdelta(start, end, delta):
                curr = start
                while curr < end:
                    yield curr
                    curr += delta
            date_range = []

            for result in perdelta(start, end, timedelta(days=1)):
                for hour in range(24):
                    date_range.append('{}-{}'.format(str(result), hour))
            return date_range

        def try_load(path):
            """
            Tries to load .gz file, and returns empty rdd if error comes up (e.g. incorrect header check)
            """
            rdd = spark.read.json(path)
            try:
                rdd.first()
                return rdd
            except:
                return spark.emptyRDD()

        spark = spark_session()
        date_times = generate_date_range(date(2015,1,1), date(2016,12,31))

        data = try_load('{}{}.json.gz'.format(config.BUCKET_LOCATION, date_times[0]))
        for date_time in date_times:
            data = data.union(try_load('{}{}.json.gz'.format(config.BUCKET_LOCATION, date_time)))

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
            year_month,
            RANK() OVER (PARTITION BY year_month ORDER BY n_events DESC) AS year_month_rank,
            repo_id,
            repo_name,
            n_events,
            n_actors
        FROM (
            SELECT
                SUBSTRING(created_at, 1, 7) as year_month,
                repo.id as repo_id,
                repo.name as repo_name,
                COUNT(*) as n_events,
                COUNT(DISTINCT actor) as n_actors
            FROM events
            GROUP BY SUBSTRING(created_at, 1, 7), repo
        ) AS createStats
    """)
    return stats

def get():
    """
    Wrapper function to construct stat RDDs
    """
    events = parse_events()
    events.registerTempTable('events')
    stats = calc_stats()

    return stats
