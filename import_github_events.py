'''
Creates a MongoDB collection using the events data from githubarchive.org

It:
1. downloads all files between two date ranges, 
2. extracts them
3. imports them
4. cleans up the mongo db using the cleanup_mongodb.py module
5. removes the downloaded JSON file
'''

import subprocess
import traceback
import logging

from datetime import datetime, timedelta
from dateutil.rrule import rrule, HOURLY

FROM_HOUR = datetime(2015,3,2,0,0,0)
TO_HOUR = datetime(2015,4,30,23,0,0)

def get_json_file_names(from_hour, to_hour):
    json_files = []

    for h in get_hourly_timestamps(from_hour, to_hour):
        json_files.append('%s-%s-%s-%s.json.gz' % (
                h.year, 
                str(h.month).rjust(2,'0'), 
                str(h.day).rjust(2,'0'), 
                str(h.hour).rjust(2,'0')
                ))
    
    return json_files

def get_hourly_timestamps(from_hour, to_hour):
    return list(rrule(HOURLY, dtstart=FROM_HOUR, until=TO_HOUR))

def main():

    logging.basicConfig(filename='import.log', 
            level=logging.DEBUG, 
            format='%(asctime)s %(message)s', 
            datefmt='%m/%d/%Y %I:%M:%S %p')

    wget_log = open('wget_log.log','w+')
    try:
        for f in get_json_file_names(FROM_HOUR, TO_HOUR):
            wget_command = [
                    'wget',
                    '-c', #so that we continue existing downloads
                    'http://data.githubarchive.org/%s' % f,
                    '-P',
                    '/tmp',
                    ]
            gunzip_command = [
                    'gunzip',
                    '-f',
                    '-v',
                    '/tmp/%s' % f,
                    ]
            import_command = [
                  'mongoimport',
                  '-d',
                  "github-edu-effectiveness",
                  '-c',
                  "events",
                  "/tmp/%s" % f.rstrip('.gz')
                  ]
            db_docs_count_command = [
                 'mongo',
                 'github-edu-effectiveness',
                 '--eval',
                 'db.events.count()'
                 ]
            rm_command = [
                 'rm',
                 '-v',
                 "/tmp/%s" % f.rstrip('.gz')
                 ]

            logging.info("Downloading: %s", f)
            exit_code = subprocess.call(wget_command, stdout=wget_log, stderr=wget_log)
            if exit_code == 8: #problem while downloading file
                logging.error("Error while downloading %s. Possibly no data archive exists for that hour. Skipping", f)
                continue
            elif exit_code == 4 or exit_code == 7: #network problem or protocol error
                logging.critical("Network problem while downloading %s. Sleeping and trying again in 10 seconds", f)
                sleep(10)
                exit_code = subprocess.call(wget_command, stdout=wget_log, stderr=wget_log)
                logging.critical("Exit code of restarted wget process is %s", exit_code)
            elif exit_code == 3:
                logging.critical("Problem while trying to save %s to disk. Check disk usage! EXITING NOW!", f)
                break
            else:
                logging.info("File %s successfully downloaded", f)
            
            logging.info("Decompressing %s", f)
            output = subprocess.check_output(gunzip_command) 
            logging.debug('%s', output)

            logging.info("Importing in MongoDB from %s", f.rstrip('.gz'))
            output = subprocess.check_output(import_command)
            logging.debug('%s', output)

            logging.info("Counting events AFTER import")
            output = subprocess.check_output(db_docs_count_command)
            logging.debug("%s", output)

            logging.info("Cleaning up the MongoDB docs in which we aren't interested")
            from cleanup_mongodb import cleanup
            result = cleanup('github-edu-effectiveness','events')
            logging.debug("Cleanup result : %s", result)
           
            logging.info("Counting events AFTER cleanup")
            output = subprocess.check_output(db_docs_count_command)
            logging.debug("%s", output)
 
            logging.info("Removing the file %s",f.rstrip('.gz'))
            output = subprocess.check_output(rm_command)
            logging.debug('%s', output)
    
    except Exception as e:
            logging.critical(e)
            logging.critical(traceback.format_exc())
            print e
            print traceback.format_exc()

if __name__ == '__main__':
    main()
