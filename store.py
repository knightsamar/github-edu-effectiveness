#builds a db store using the Github data
import github
from pymongo import MongoClient

'''
Why do we store the data when we can get it from GitHub API anytime we need?

1. Because GitHub API seems to say that we can get data only as old as 90 days in case of things like Events. 
We often need data older than that.

2. Querying the GitHub API for things specifically often doesn't work. Say, get all Events where type is CommentCommitEvent
It is easier to do that using a local db store like MongoDB
'''

def connect(dbname='github-edu-effectiveness'):
    '''Connects and returns a Database object for use'''
    c = MongoClient()
    db = c[dbname]
    return db

def store_events_for_user(u):
    '''
    Gets and stores all the events for a given user
    '''
    
    print "Storing events for user", u
    events_collection = connect()['events']

    events_from_github = u.get_events()
    print type(events_from_github)

    for e in events_from_github:
        print "Storing event", e
        x = events_collection.insert_one(e._rawData)
        print "Stored at ", x.inserted_id

    del(x)

