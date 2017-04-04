import config
from agg_stats import get as get_agg_stats

def get():
    """
    Returns aggregate stats for all repos
    """
    stats = get_agg_stats()
    print(stats.first())
    return stats

def corr(stats):
    """
    Returns pearson r of n_actors v. edit_size
    """
    corr = stats.stat.corr('n_actors', 'edit_size')
    return corr

stats = get()
stats.collect()
stats.write.csv(config.BUCKET_LOCATION + '/Results/q3a.csv')

corr = corr(stats)
print(corr)
