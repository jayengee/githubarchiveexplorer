from top_10s_records import get as get_top_10s_records

def get():
    """
    Returns the top 10 repos, based on the highest monthly event counts for that repo, all time
    """
    top_10_stats = get_top_10s_records()
    top_10_monthly_all_time = top_10_stats.orderBy(top_10_stats.peak_n_events.desc()).limit(10)

    return top_10_monthly_all_time

get().collect()
