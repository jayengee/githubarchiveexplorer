# Github Archive Explorer

### Overview
PySpark exploration/learning project - utilizing Spark to explore data made available by the GitHub Archive project

### Research Questions
This project is designed to answer the following research questions:

1. Over the years, on a monthly basis, what are the top 10 javascript repos people interact with (committed, starred, forked, etc)?
2. If we track these repos ever made to the monthly top 10 list, can we update how active the repos are based on its peak number of interactions? This way, we can learn how live these repos are.
3. If we look into how people are communicating in Github through commits, reviews, comments, etc in these repos, can we find out the distribution of the member cluster size and how it is related to the number of lines per member would merge?

### Approach (WIP)
Given the nature of the project, we will be tackling the work involved via two different sets of functions

#### `extract`
This set of functions is used to `wget` the .gzipped `.json` files containing the events data for each hour of each day, within a specified date range, from the [GitHub Archive](https://www.githubarchive.org/).

The functions can be triggered by running the `get_files()` function in the module. If no date ranges are passed, the function grabs data from the entire 2011 to 2016 date range.

WIP - The grabber currently `wgets` the files to a local directory. Given the system we are aiming for, we will likely need to refactor the grabber to forward to files to a dedicated S3 bucket, and remove the local file.

#### `transform_and_load`
This set of functions loads the events data into an Apache Spark instance, leaning on the PySpark module bundled alongside Spark.

A larger help function creates an RDD of all the files downloaded by `extract`, then subsets the appropriate events into another RDD and returns it. Query actions, using PySpark's SparkSQL module, are then performed on the returned RDD to answer appropriate research questions.

##### Schema
The schema for GitHub events can be found [here](https://developer.github.com/v3/activity/events/types/).

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

### Setup
#### PySpark
Since `pyspark` is not currently installable via `pip`, `findspark` is used to locate the local installation directory.

#### Spark
As of the current iteration, Spark is being run locally with no additional configurations. This will change in future iterations.
