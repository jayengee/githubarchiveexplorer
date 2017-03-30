from datetime import date, datetime, timedelta
import os
import shutil
import sys
from utils import storage_client
import wget

def generate_file_url(filename):
    """
    Takes a datehour string and generates url for the matching GitHub Archive
    gzip file
    """

    date_string = date
    url = 'http://data.githubarchive.org/{}'.format(filename)
    return url

def wget_file(url):
    """
    Downloads file at provided url to local /files/ directory
    """
    wget.download(url, './files/')

def generate_date_range(start, end):
    """
    For a given pair of start and end date objects, returns list of strings
    matching the year, month, day, hour format used by GitHub Archive
    """
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

def get_date_range_files(date_range):
    """
    For a given list of date strings, loops over them and grabs the file from
    GitHub Archive
    """
    bucket = storage_client()
    file_count = 0

    try:
        for date in date_range:
            filename = '{}.json.gz'.format(date)
            file_url = generate_file_url(filename)
            wget_file(file_url)
            blob = bucket.blob(filename)
            blob.upload_from_filename('./files/{}'.format(filename))
            file_count += 1

            # if file_count >= (24):
            #     shutil.rmtree('./files/')
            #     os.makedirs('./files/')
    except:
        print('Unexpected error: {}'.format(sys.exc_info()[0]))
        print('   Failed on file: {}'.format(filename))

def get_files(startdate = None, enddate = None):
    """
    Larger wrapper function for grabbing all necessary data
    """
    if startdate is None:
        startdate = date(2011, 1, 1)
    if enddate is None:
        enddate = date(2017, 1, 1)

    date_range = generate_date_range(startdate, enddate)
    print(date_range)
    get_date_range_files(date_range)
