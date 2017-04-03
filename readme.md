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
Spark tasks are coded in PySpark, and sent to a Spark master node to kick off the appropriate tasks

## Deployment
This particular project was launched on Google Cloud, leveraging the following:
- Compute Engine
  - To run `extract` and trigger PySpark tasks
- Cloud Storage Standard
  - To store ``.json.gz` log files, as well as results from PySpark tasks
- Cloud Dataproc
  - One master, and a number of worker nodes, with Spark pre-installed

### Compute Engine
1. Install [`gcloud`](https://cloud.google.com/sdk/downloads#apt-get) authentication tool on
2. Run initialization to set up connections to other boxes with `gcloud init`
3. `git clone` this repo
4. Install Python
5. Install repo dependencies:
    ```
    githubArchiveExplorer$ pip install -r requirements.txt
    ```
6. Update various project, cluster, and bucket variables in `config.py` if necessary, based on project setup

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

The grabber current `wgets` the file for each hour to a local directory, then, using the `google-cloud` module, copies the file to a remote bucket. After each day's worth of files have been copied over, the local directory is wiped, so as to keep storage usage on the Compute Engine low.

#### Running Spark tasks
Spark tests are currently sent from the Compute Engine to the Spark Master Node via command line, and may be optimized to run via a script in the future.

Leveraging the `gcloud` library, a request is sent to the Spark Master Node by sending the appropriate task `.py` file, along with additional `.py` files that contain the various modules imported by the task `.py` file. These task `.py` files are broken out by resarch question, though some of them have been consolidated to reduce overhead when calling the appropriate tasks.

##### Questions 1 and 2
On the Compute Engine, run the following:
```
githubArchiveExplorer$ gcloud dataproc jobs submit pyspark --cluster spark-cluster --py-files config.py,pyspark_jobs/monthly_stats.py pyspark_jobs/q1_and_q2.py
```

##### Question 3
On the Compute Engine, run the following:
```
githubArchiveExplorer$ gcloud dataproc jobs submit pyspark --cluster spark-cluster --py-files config.py,pyspark_jobs/agg_stats.py pyspark_jobs/q3.py
```

#### Accessing results
Spark task status can be monitored via the cluster details tab under the Cloud Dataproc part of the Google Console

Results can be found within the Cloud Storage Bucket, under the `Results` sub-directory.

##### Format
Spark natively exports results in parts, taking advantage of different worker nodes to do so. This means numerous `.csv` files exported for each task.

To get around additional work to read, parse, and re-merge these files, `coalesce(1)` is run on export, but as data sizes increase, this may not be feasible in the future.

## Schema
### GitHub events schema
The schema for GitHub events can be found [here](https://developer.github.com/v3/activity/events/types/).

Given the [schema change](https://www.reddit.com/r/bigquery/comments/2s80y3/github_archive_changes_monthly_and_daily_tables/) that occurred starting with 2015 data, ingestion rules are different for pre and post 2015 events data.

While working on this project, however, it seems that githubarchive's data for pre 2015 no longer abides by the old `timeline` schema, where `repository` (and as a result, `respository.language`) was accessible at the base event level. In fact, with the exception that some keys are now missing, the schema for pre-2015 events data now resembles that of post 2015 data. As a result, we have chosen to exclude pre-2015 events data until the appropriate keys are populated or can be found.

Given the loss of repository language information in events other than `PullRequestEvents`, all post-2015 data is limited to that event type for this project.

To standardize for this, and to answer the research questions outlined for this project, the following two schemas have been put together to appropriately capture statistics for repos across time:

### Monthly stats schema
This schema rolls up certain stats at the month level, and captures, as well, the rank of the repo's engagement over the course of the month

column | type | description
-------|------|------------
year_month | string | year and month of stats (e.g. '2014-04')
year_month_rank | int | repo rank of n_events, within year and month
repo_id | string | repo's id. For pre-2015 events, this is a string, whereas for post, this is an int
repo_name | string | repo's name
n_events | int | number of qualifying events for repo, within year and month
n_actors | int | number of unique actors for the qualifying events for repo, within year and month

### Aggregate stats schema
This schema rolls up certain stats all time

column | type | description
-------|------|------------
repo_id | string | repo's id. For pre-2015 events, this is a string, whereas for post, this is an int
repo_name | string | repo's name
n_events | int | number of qualifying events for repo
n_additions | int | number of lines of code added over time
n_deletions | int | number of lines of code removed over time
edit_size | int | number of lines of code modified over time (added and removed)
n_actors | int | number of unique actors for the qualifying events for repo

## Research Questions
This project is designed to answer the following research questions:

1. Over the years, on a monthly basis, what are the top 10 javascript repos people interact with (committed, starred, forked, etc)?
2. If we track these repos ever made to the monthly top 10 list, can we update how active the repos are based on its peak number of interactions? This way, we can learn how live these repos are.
3. If we look into how people are communicating in Github through commits, reviews, comments, etc in these repos, can we find out the distribution of the member cluster size and how it is related to the number of lines per member would merge?

## Authors
- Jason Ng [@jayengee](https://github.com/jayengee)

## Acknowledgements
- Michael Zhang
- Mads Hartmann: [_http://mads-hartmann.com/2015/02/05/github-archive.html_](http://mads-hartmann.com/2015/02/05/github-archive.html)
- [Githut](https://github.com/littleark/githut)
- Stephen O'Grady: [_The RedMonk Programming Language Rankings: January 2017_](http://redmonk.com/sogrady/2017/03/17/language-rankings-1-17/)
