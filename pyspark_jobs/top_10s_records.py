from monthly_top_10s import get as get_monthly_top_10s

def get():
    """
    Returns max monthly event counts for any repo ever ranked in the top 10 most active
    repos
    """
    top_10s = get_monthly_top_10s()
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

get().collect()
