import config
from monthly_stats import get as get_monthly_stats, spark_session as spark

def get_monthly_top_10s():
    """
    Returns top 10 most active ranked repos by month, based on event counts
    """
    stats = get_monthly_stats()
    print(stats.first())
    top_10_monthlies = stats.where(stats.year_month_rank <= 10)
    top_10_monthlies.registerTempTable('top_10_monthlies')
    return top_10_monthlies

def get_top_10s_records():
    """
    Returns max monthly event counts for any repo ever ranked in the top 10 most active
    repos
    """
    stats = get_monthly_stats()
    top_10s = get_monthly_top_10s()
    top_10_ids = [int(i.repo_id) for i in top_10s.select(top_10s.repo_id).distinct().collect()]
    top_10_stats = stats.where(stats.repo_id.isin(top_10_ids))
    top_10_stats.registerTempTable('top_10_stats')
    top_10s_records = spark().sql("""
        SELECT
            repo_id,
            repo_name,
            MAX(n_events) AS peak_n_events
        FROM top_10_stats
        GROUP BY repo_id, repo_name
    """)
    return top_10s_records

def get_top_10_all_time():
    """
    Returns the top 10 repos, based on the highest monthly event counts for that repo, all time
    """
    top_10_stats = get_top_10s_records()
    top_10_monthly_all_time = top_10_stats.orderBy(top_10_stats.peak_n_events.desc()).limit(10)

    return top_10_monthly_all_time

monthly_top_10s = get_monthly_top_10s()
monthly_top_10s.coalesce(1).collect()
monthly_top_10s.write.csv(config.BUCKET_LOCATION + '/Results/q1.csv')

top_10s_records = get_top_10s_records()
top_10s_records.coalesce(1).collect()
top_10s_records.write.csv(config.BUCKET_LOCATION + '/Results/q2a.csv')

top_10_all_time = get_top_10_all_time()
top_10_all_time.coalesce(1).collect()
top_10_all_time.write.csv(config.BUCKET_LOCATION + '/Results/q2b.csv')
