from config import sparkSession
import json

def parse_pre_2015_events():
    def read_files():
        spark = sparkSession()
        data = spark.read.json('./files/2014-*')
        data = data.filter(data.repository.language == 'JavaScript')
        for year in ['2014']:
            data = data.union(spark.read.json('./files/{}-*'.format(year)))
        return data

    def parse_creates():
        spark = sparkSession()
        creates = data.filter(data.type == 'CreateEvent') #TODO date is busted
        creates = creates.filter((creates.payload.ref_type == 'branch') |
            (creates.payload.ref_type == 'repository')
        )
        return creates

    def parse_forks():
        forks = data.filter(data.type == 'DeploymentEvent')
        return forks

    def parse_pull_requests():
        pull_requests = data.filter(data.type == 'PullRequestEvent')
        pull_requests = pull_requests.filter((pull_requests.payload.action == 'opened') |
            ((pull_requests.payload.action == 'closed') & (pull_requests.payload.pull_request.merged == True))
        )
        return pull_requests

    def parse_pushes():
        pushes = data.filter(data.type == 'PushEvent')
        return pushes

    data = read_files()

    event_types = [
        parse_creates(),
        parse_forks(),
        parse_pull_requests(),
        parse_pushes()
    ]

    events = event_types[0]

    for event_type_index in range(1, len(event_types)):
        events = events.union(event_types[event_type_index])

    return events

def calc_pre_2015_stats(events):
    spark = sparkSession()
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
                repository.id as repo_id,
                repository.name as repo_name,
                COUNT(*) as n_events,
                COUNT(DISTINCT actor) as n_actors
            FROM pre_2015_events
            GROUP BY SUBSTRING(created_at, 1, 7), repository
        ) AS createStats
        HAVING year_month_rank <= 10
    """)
    return stats

def parse_post_2015_events():
    def read_files():
        spark = sparkSession()
        data = spark.read.json('./files/2015-*')
        for year in ['2016']:
            data = data.union(spark.read.json('./files/{}-*'.format(year)))
        return data

    def parse_pull_requests():
        pull_requests = data.filter(data.type == 'PullRequestEvent')
        pull_requests = pull_requests.filter(pull_requests.payload.pull_request.base.repo.language == 'JavaScript')
        return pull_requests

    data = read_files()
    pull_requests = parse_pull_requests()

    events = pull_requests

    return events

def calc_post_2015_stats(events):
    spark = sparkSession()
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
                COUNT(DISTINCT actor.id) as n_actors
            FROM post_2015_events
            GROUP BY SUBSTRING(created_at, 1, 7), repo
        ) AS createStats
        HAVING year_month_rank <= 10
    """)
    return stats

def get_stats():
    pre_2015_events = parse_pre_2015_events()
    pre_2015_events.registerTempTable('pre_2015_events')
    pre_2015_stats = calc_pre_2015_stats(pre_2015_events)

    post_2015_events = parse_post_2015_events()
    post_2015_events.registerTempTable('post_2015_events')
    post_2015_stats = calc_post_2015_stats(post_2015_events)

    return pre_2015_stats.union(post_2015_stats)
