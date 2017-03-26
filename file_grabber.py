import gzip
from datetime import date, datetime, timedelta
import wget

def generate_file_url(date):
    date_string = date
    url = 'http://data.githubarchive.org/{}.json.gz'.format(date_string)
    return url

def get_file(url):
    wget.download(url, './files/')

def generate_date_range(start, end):
    def perdelta(start, end, delta):
        curr = start
        while curr < end:
            yield curr
            curr += delta
    date_range = []

    for result in perdelta(start, end, timedelta(days=1)):
        for hour in range(24):
            date_range.append('{}-{}'.format(str(result), hour))
    return date_range

def ingest_date_range_files(date_range):
    for date in date_range:
        file_url = generate_file_url(date)
        get_file(file_url)

date_range = generate_date_range(date(2014, 11, 1), date(2014, 11, 5))
print(date_range)
ingest_date_range_files(date_range)
