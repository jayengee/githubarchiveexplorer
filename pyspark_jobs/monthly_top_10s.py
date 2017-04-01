import monthly_stats

def get():
    """
    Returns top 10 most active ranked repos by month, based on event counts
    """
    stats = monthly_stats.get_stats()
    print(stats.first())
    top_10_monthlies = stats.where(stats.year_month_rank <= 10)
    top_10_monthlies.registerTempTable('top_10_monthlies')
    return top_10_monthlies

get().collect()
