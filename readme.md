# Github Archive Explorer
PySpark exploration/learning project - utilizing Spark to explore data made available by the GitHub Archive project

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
#### Python
This code was written for Python3. Ensure that the box this is being run on has Python3 installed

#### Spark
As of the current iteration, Spark is being run locally with no additional configurations. This will change in future iterations.

To install Spark on OSX, install via `brew`:
```
$ brew install apache-spark
```
On Ubuntu, `wget` the appropriate version of Spark listed on the [downloads](http://spark.apache.org/downloads.html) section of the site, and untar the file to the directory of choice

*NOTE*: Spark has a number of requirements, including Java. For information, refer to the [official API docs](https://spark.apache.org/docs/latest/index.html) and for more information

#### PySpark
Since `pyspark` is not currently installable via `pip`, `findspark` is used to locate the local installation directory. This requirement is covered by `pip`

### Installing
Clone this repo to the desired directory on the machine to be used for interacting with the GitHub Archive data.

Dependencies can be installed by running `pip`:
```
githubArchiveExplorer$ pip install -r requirements.txt
```

## Deployment
_Coming soon_

## Usage
#### `extract`
This set of functions is used to `wget` the .gzipped `.json` files containing the events data for each hour of each day, within a specified date range, from the [GitHub Archive](https://www.githubarchive.org/).

The functions can be triggered by running the `get_files()` function in the module. If no date ranges are passed, the function grabs data from the entire 2011 to 2016 date range.

To get all data from Jan 2011
```
> import extract
> from datetime import date
> extract.get_files(date(2011, 1, 1), date(2011, 2, 1))
```

To get all data from Jan 2011 to Dec 2016
```
> import extract
> from datetime import date
> extract.get_files()
```

WIP - The grabber currently `wgets` the files to a local directory. Given the system we are aiming for, we will likely need to refactor the grabber to forward to files to a dedicated S3 bucket, and remove the local file.

#### `transform_and_load`
This set of functions loads the events data into an Apache Spark instance, leaning on the PySpark module bundled alongside Spark.

A larger help function creates an RDD of all the files downloaded by `extract`, then subsets the appropriate events into another RDD and returns it. Query actions, using PySpark's SparkSQL module, are then performed on the returned RDD to answer appropriate research questions.

To get all engagement stats:
```
> import transform_and_load
> stats = transform_and_load.get_stats()
> stats
DataFrame[year_month: string, year_month_rank: int, repo_id: bigint, repo_name: string, n_events: bigint, n_actors: bigint]
> stats.first()
Row(year_month=u'2014-11', year_month_rank=1, repo_id=22945468, repo_name=u'noop-sewi', n_events=8, n_actors=1)
```

To get monthly top 10 repos:
```
> import transform_and_load
> monthly_top_10s = transform_and_load.get_monthly_top_10s()
> monthly_top_10s
DataFrame[year_month: string, year_month_rank: int, repo_id: bigint, repo_name: string, n_events: bigint, n_actors: bigint]
```

To get peak monthly stats for all monthly top 10 repos:
```
> import transform_and_load
> top_10_records = transform_and_load.get_top_10s_records()
> top_10_records
DataFrame[year_month: string, year_month_rank: int, repo_id: bigint, repo_name: string, n_events: bigint, n_actors: bigint]
```

To get all-time monthly top 10 repos:
```
> import transform_and_load
> all_time_top_10s = transform_and_load.top_10_monthly_all_time()
> all_time_top_10s
DataFrame[year_month: string, year_month_rank: int, repo_id: bigint, repo_name: string, n_events: bigint, n_actors: bigint]
```

## Schema
### GitHub events schema
The schema for GitHub events can be found [here](https://developer.github.com/v3/activity/events/types/).

### Stats schema
Given the [schema change](https://www.reddit.com/r/bigquery/comments/2s80y3/github_archive_changes_monthly_and_daily_tables/) that occurred starting with 2015 data, ingestion rules are different for pre and post 2015 events data. Given the loss of repository language information in events other than `PullRequestEvents`, all post-2015 data is limited to that event type for this project.

To standardize for this, and to answer the research questions outlined for this project, the following schema is to capture event statistics for repos across time:

column | type | description
-------|------|------------
year_month | string | year and month of stats (e.g. '2014-04')
year_month_rank | int | repo rank of n_events, within year and month
repo_id | string | repo's id. For pre-2015 events, this is a string, whereas for post, this is an int
repo_name | string | repo's name
n_events | int | number of qualifying events for repo, within year and month
n_actors | int | number of unique actors for the qualifying events for repo, within year and month

## Research Questions
This project is designed to answer the following research questions:

1. Over the years, on a monthly basis, what are the top 10 javascript repos people interact with (committed, starred, forked, etc)?
2. If we track these repos ever made to the monthly top 10 list, can we update how active the repos are based on its peak number of interactions? This way, we can learn how live these repos are.
3. If we look into how people are communicating in Github through commits, reviews, comments, etc in these repos, can we find out the distribution of the member cluster size and how it is related to the number of lines per member would merge?

### Approach (WIP)
Given the nature of the project, we will be tackling the work involved via two different sets of functions

## Authors
- Jason Ng [@jayengee](https://github.com/jayengee)

## Acknowledgements
- Michael Zhang
- Mads Hartmann: [_http://mads-hartmann.com/2015/02/05/github-archive.html_](http://mads-hartmann.com/2015/02/05/github-archive.html)
- [Githut](https://github.com/littleark/githut)
- Stephen O'Grady: [_The RedMonk Programming Language Rankings: January 2017_](http://redmonk.com/sogrady/2017/03/17/language-rankings-1-17/)
