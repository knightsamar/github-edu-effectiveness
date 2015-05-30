'''
This is used to cleanup a MongoDB database created from JSON files at githubarchive.org
It deletes all documents EXCEPT for those which contain events performed by the users
whom we are interested in
'''
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import csv
from pprint import pprint

def list_our_interesting_users():
    with open('forks.csv','r') as fcsv:
        forks = csv.DictReader(fcsv)
        list_of_users = [f['owner_username'] for f in forks]
        return list_of_users

def cleanup(db, collection):
    c = MongoClient()
    db = c[db]
    coll = db[collection]
    list_of_users_not_to_remove = list_our_interesting_users()
    try:
        bulk = coll.initialize_ordered_bulk_op()
        #events received BEFORE 31st Dec 2014 seem to have actor as a string containing the login name
        bulk.find({ 'actor' : { 
                        '$type' : 2, #actor is a string instead of array 
                        '$nin'  : list_of_users_not_to_remove #actor is a login which does NOT match any of our interested usernames
                        }
                 }).remove()
        #events received AFTER 31st Dec 2014 seem to have actor as an array containing an attribute called login.
        bulk.find({ 'actor.login'   : {
                        '$exists'   : 'true',
                        '$nin'      : list_of_users_not_to_remove #actor is a login which does NOT match any of our interested usernames
                        }
                }).remove()
        result = bulk.execute()
    except BulkWriteError as bwe:
            pprint(bwe.details)
            print bwe
            return bwe

    pprint(result)
    return result

if __name__ == '__main__':
    cleanup()
