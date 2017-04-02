import config
from agg_stats import get as get_agg_stats

def get():
    """
    Returns top 10 most active ranked repos by month, based on event counts
    """
    stats = get_agg_stats()
    print(stats.first())
    corr = stats.stat.corr('n_actors', 'edit_size')
    return corr

results = get()
results.collect()
results.write.csv(config.BUCKET_LOCATION + '/Results/q3.csv')
