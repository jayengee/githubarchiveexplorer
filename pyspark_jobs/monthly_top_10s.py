import config
from monthly_stats import get as get_monthly_stats

def get():
    """
    Returns top 10 most active ranked repos by month, based on event counts
    """
    stats = get_monthly_stats()
    print(stats.first())
    top_10_monthlies = stats.where(stats.year_month_rank <= 10)
    top_10_monthlies.registerTempTable('top_10_monthlies')
    return top_10_monthlies

results = get()
results.collect()
results.write.csv(config.BUCKET_LOCATION + '/Results/monthly_top_10s.csv')
