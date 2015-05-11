import github
from github import Github
from utils import get_all_related_repos, get_all_commits_on_repos, get_all_pull_requests, tzutc, tzlocal, get_events_aggregates_for_user
import csv
from store import store_events_for_user

class GithubInfo:
    r = None
    repos = {}
    commits = {}
    pull_requests = {}
    g = None

    def __init__(self, login = '', password = '', user = 'gayatrivenugopal', repo = "MobileTechnologies"):
        self.g = Github(login_or_token=login, password=password) #Use your username and password for getting over rate limit.
        self.r = self.g.get_user(user).get_repo(repo)

    def forks_info(self):
        self.repos = get_all_related_repos(self.r)
        with open('forks.csv','w') as fcsv:
            fieldnames = ['owner', 'repo', 'created_at', 'forked_from_repo_by']
            w = csv.DictWriter(fcsv, fieldnames)

            w.writeheader()
            for o,r in self.repos.items():
                created_at_ist = r.created_at.replace(tzinfo=tzutc()).astimezone(tzlocal()).ctime()
                w.writerow({'owner':o, 'repo':r.name, 'created_at': created_at_ist, 'forked_from_repo_by':r.source.owner.login})

            fcsv.flush()

    def commits_info(self):
        self.commits = get_all_commits_on_repos(self.repos)

        with open('commits.csv','w') as ccsv:
            fieldnames = ['sha', 'author', 'committer', 'repo','repo_url', 'date', 'comment',]
            w = csv.DictWriter(ccsv, fieldnames)
        
            w.writeheader()
            for sha,commit in self.commits.items():
                w.writerow({'sha': sha, 'author':commit['author'], 'committer': commit['committer'], 'repo' : commit['repo'], 'repo_url' : commit['repo_url'], 'date': commit['date'], 'comment': commit['comment']})

            ccsv.flush()

    def pull_request_info(self):
        self.pull_requests = get_all_pull_requests(self.r)

        with open('pull_requests.csv','w') as prcsv:
            fieldnames = ['id','user','created_at','closed_at', 'additions', 'deletions', 'changed_files', 'review_comments','merged']
            w = csv.DictWriter(prcsv, fieldnames)
        
            w.writeheader()
            for i,pr in self.pull_requests.items(): #because id is a built-in function, we use the variable i
                w.writerow({'id': i, 'user': pr['user'], 'created_at': pr['created_at'], 'closed_at' : pr['closed_at'], 'additions':pr['additions'], 'deletions':pr['deletions'], 'changed_files': pr['changed_files'], 'review_comments' : pr['review_comments'], 'merged' : pr['merged']})

            prcsv.flush()

    def store_all_user_events_info(self):
        '''
        Stores ALL events of ALL 'relevant' users

        In this case relevant users are all those users who have forked our original repo.
        '''
        with open('forks.csv','r') as fcsv:
            forks = csv.DictReader(fcsv)

            for f in forks:
                try:
                    u = self.g.get_user(f['owner'])

                    if type(u) is not github.NamedUser.NamedUser:
                        print "ERROR: Cannot process ",f
                        continue

                    print u
                    store_events_for_user(u)
                except Exception as e:
                    print e


    def get_all_user_events(self):
        #get all types of aggregates that are available
        fieldnames = get_events_aggregates_for_user(None)
        fieldnames.append('user')

        #get figure for each user
        with open('forks.csv','r') as fcsv:
            forks = csv.DictReader(fcsv)
            for f in forks:
                try:
                    #STEP 1: get an user
                    u = self.g.get_user(f['owner'])

                    if type(u) is not github.NamedUser.NamedUser:
                        print "ERROR: Cannot process ",f
                        continue

                    #STEP 2: get all event aggregates for that user
                    event_aggregates = {'user' : u.login}
                    event_aggregates.update(get_events_aggregates_for_user(u))

                    #STEP 3: write down all the event aggregates in csv
                    with open('user_events.csv','a') as uecsv:
                        w = csv.DictWriter(uecsv, fieldnames, restval=0)
                        w.writeheader()
                        w.writerow(event_aggregates)

                        uecsv.flush()
                except Exception as e:
                    print e

if __name__ == "__main__":
    
    #Initiate API connection
    #specify a username and password to get over the rate limit of GitHub API
    gi = GithubInfo(login = '', password = '', user = 'gayatrivenugopal', repo = 'MobileTechnologies') #Initate our Info gatherer

    #gi.forks_info()
    #gi.commits_info()
    #gi.pull_request_info()
    #gi.get_all_forkers()
    #gi.store_all_user_events_info()
    gi.get_all_user_events()
