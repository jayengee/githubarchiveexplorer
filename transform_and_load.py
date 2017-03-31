import config
import json
import pyspark

def spark_session():
    return pyspark.sql.SparkSession \
        .builder \
        .appName(config.APP_NAME) \
        .enableHiveSupport() \
        .getOrCreate()

def parse_pre_2015_events():
    """
    Reads all json.gz files from before 2015 into one RDD, subsets into
    smaller RDDs based on rules for different types of events, and ultimately
    returns a RDD of the union of them
    """

    def read_files():
        """
        Reads all json.gz files from 2011 to 2014 and unions them. Filters by
        repository language (since this was available at this point in the
        schema), then returns the resuting RDD
        """
        spark = spark_session()
        years = ['2011', '2012', '2013', '2014']
        data = spark.read.json('{}{}-*'.format(config.BUCKET_LOCATION, years[0]))
        for year in years:
            data = data.union(spark.read.json('./files/{}-*'.format(year)))

        return data

    def parse_pull_requests():
        """
        Reads from larger data RDD and returns subset of events that match the
        criteria for appropraite PullRequestEvents (we are only capturing PR
        open and successful merge events)
        """
        pull_requests = data.filter(data.type == 'PullRequestEvent')
        pull_requests = pull_requests.filter(pull_requests.payload.pull_request.base.repo.language == 'JavaScript')
        return pull_requests

    data = read_files()

    return parse_pull_requests()

def calc_pre_2015_stats(events):
    """
    Determine n_events and n_actors for 10 repos with the most events each month
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
            FROM pre_2015_events
            GROUP BY SUBSTRING(created_at, 1, 7), repository
        ) AS createStats
    """)
    return stats

def parse_post_2015_events():
    """
    Reads all json.gz files from from 2015 onwards into one RDD, subsets into
    smaller RDDs based on rules for different types of events, and ultimately
    returns a RDD of the union of them
    """
    def read_files():
        """
        Reads all json.gz files from 2015 to 2016 and unions them, then returns
        the resuting RDD
        """
        spark = spark_session()
        years = ['2015', '2016']
        data = spark.read.json('{}{}-*'.format(config.BUCKET_LOCATION, years[0]))
        for year in years:
            data = data.union(spark.read.json('./files/{}-*'.format(year)))

        return data

    def parse_pull_requests():
        """
        Reads from larger data RDD and returns subset of events that match the
        criteria for appropriate PullRequestEvents (we are only capturing PR
        open and successful merge events). Also, due to the change in schema,
        only pull request events contain the repo language, and thus will be
        the only source of events for 2015 onwards for this project
        """
        pull_requests = data.filter(data.type == 'PullRequestEvent')
        pull_requests = pull_requests.filter(pull_requests.payload.pull_request.base.repo.language == 'JavaScript')
        return pull_requests

    data = read_files()

    return parse_pull_requests()

def calc_post_2015_stats(events):
    """
    Determine n_events and n_actors for 10 repos with the most events each month
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
            FROM post_2015_events
            GROUP BY SUBSTRING(created_at, 1, 7), repo
        ) AS createStats
    """)
    return stats

def get_stats():
    """
    Wrapper function to construct stat RDDs
    """
    pre_2015_events = parse_pre_2015_events()
    pre_2015_events.registerTempTable('pre_2015_events')
    pre_2015_stats = calc_pre_2015_stats(pre_2015_events)

    post_2015_events = parse_post_2015_events()
    post_2015_events.registerTempTable('post_2015_events')
    post_2015_stats = calc_post_2015_stats(post_2015_events)

    return pre_2015_stats.union(post_2015_stats)

def get_monthly_top_10s():
    """
    Returns top 10 most active ranked repos by month, based on event counts
    """
    stats = get_stats()
    top_10_monthlies = stats.where(stats.year_month_rank <= 10)
    top_10_monthlies.registerTempTable('top_10_monthlies')
    return top_10_monthlies

def get_top_10s_records():
    """
    Returns max monthly event counts for any repo ever ranked in the top 10 most active
    repos
    """
    stats = get_stats()
    top_10s = get_top_10_monthlies()
    top_10_ids = [int(i.repo_id) for i in top_10s.select(top_10s.repo_id).distinct().collect()]
    top_10_stats = stats.where(stats.repo_id.isin(top_10_ids))
    top_10_stats.registerTempTable('top_10_stats')
    top_10s_records = spark.sql("""
        SELECT
            repo_id,
            repo_name,
            MAX(n_events) AS peak_n_events,
        FROM top_10_stats
        GROUP BY repo_id
    """)
    return top_10s_records

def top_10_monthly_all_time():
    """
    Returns the top 10 repos, based on the highest monthly event counts for that repo, all time
    """
    top_10_stats = get_top_10s_records()
    top_10_monthly_all_time = top_10_stats.orderBy(top_10_stats.peak_n_events.desc()).limit(10)

    return top_10_monthly_all_time
