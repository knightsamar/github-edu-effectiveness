import github
from github import Github
from utils import get_all_related_repos, get_all_commits_on_repos, get_all_pull_requests, tzutc, tzlocal, get_events_aggregates_for_user
import csv
from store import store_events_for_user
import settings

class GithubInfo:
    r = None
    repos = {}
    commits = {}
    pull_requests = {}
    events_analysis = {}
    g = None

    def __init__(self,
            login = '',
            password = '',
            user = settings.COURSE_REPO_OWNER,
            repo = settings.COURSE_REPO_NAME):

        self.g = Github(login_or_token=login, password=password) #Use your username and password for getting over rate limit.
        self.r = self.g.get_user(user).get_repo(repo)

    def forks_info(self):
        print "Getting and storing info about all the forks of %s/%s in forks.csv" % (self.r.owner.login, self.r.name)

        self.repos = get_all_related_repos(self.r)
        with open('forks.csv','w') as fcsv:
            fieldnames = ['owner', 'owner_username', 'repo', 'created_at', 'forked_from_repo_by']
            w = csv.DictWriter(fcsv, fieldnames)

            w.writeheader()
            for o,r in self.repos.items():
                created_at_ist = r.created_at.replace(tzinfo=tzutc()).astimezone(tzlocal()).ctime()
                w.writerow({
                    'owner':o,
                    'owner_username': r.owner.login,
                    'repo':r.name,
                    'created_at': created_at_ist,
                    'forked_from_repo_by':r.source.owner.login
                    })

            fcsv.flush()

    def commits_info(self):
        print "Getting and storing info about all the commits of various 'interesting' users in commits.csv"
        self.commits = get_all_commits_on_repos(self.repos)

        with open('commits.csv','w') as ccsv:
            fieldnames = ['sha', 'author', 'author_username', 'committer', 'committer_username', 'repo','repo_url', 'date', 'comment',]
            w = csv.DictWriter(ccsv, fieldnames)
        
            w.writeheader()
            for sha,commit in self.commits.items():
                w.writerow({
                    'sha' : sha,
                    'author' : commit['author'],
                    'author_username' : commit['author_username'],
                    'committer' : commit['committer'],
                    'committer_username' : commit['committer_username'],
                    'repo' : commit['repo'],
                    'repo_url' : commit['repo_url'],
                    'date': commit['date'],
                    'comment': commit['comment']
                })

            ccsv.flush()

    def pull_request_info(self):
        print "Getting and storing info about all the pull requests on %s/%s in pull_requests.csv" % (self.r.owner.login, self.r.name)
        self.pull_requests = get_all_pull_requests(self.r)

        with open('pull_requests.csv','w') as prcsv:
            fieldnames = ['id','user','username','created_at','closed_at', 'additions', 'deletions', 'changed_files', 'review_comments','merged']
            w = csv.DictWriter(prcsv, fieldnames)
        
            w.writeheader()
            for i,pr in self.pull_requests.items(): #because id is a built-in function, we use the variable i
                w.writerow({
                    'id': i,
                    'user': pr['user'],
                    'username':pr['username'],
                    'created_at': pr['created_at'],
                    'closed_at' : pr['closed_at'],
                    'additions':pr['additions'],
                    'deletions':pr['deletions'],
                    'changed_files': pr['changed_files'],
                    'review_comments' : pr['review_comments'],
                    'merged' : pr['merged']
                })

            prcsv.flush()

    def store_all_user_events_info(self):
        '''
        Stores ALL events of ALL 'relevant' users

        In this case relevant users are all those users who have forked our original repo.
        '''
        print "Getting and storing info about all the events performed various 'interesting' users in a Mongodb database"

        with open('forks.csv','r') as fcsv:
            forks = csv.DictReader(fcsv)

            for f in forks:
                try:
                    u = self.g.get_user(f['owner_username'])

                    if type(u) is not github.NamedUser.NamedUser:
                        print "ERROR: Cannot process ",f
                        continue

                    print u
                    store_events_for_user(u)
                except Exception as e:
                    print e


    def get_all_user_event_aggregates(self):
        print "Getting and storing info about all the events performed various 'interesting' users from a Mongodb database to user_events.csv"

        #get all types of aggregates that are available
        fieldnames = get_events_aggregates_for_user(None)
        fieldnames.append('user')

        #get figure for each user
        with open('forks.csv','r') as fcsv:
            forks = csv.DictReader(fcsv)
            for f in forks:
                try:
                    #STEP 1: get an user
                    u = self.g.get_user(f['owner_username'])

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
    def store_all_user_events_analysis(self):
        '''
        use the event_utils module to obtain and dump JSON analysis
        of all user events for all interesting users
        '''
        from event_utils import GitHubEventsInfo

        with open('forks.csv','r') as fcsv:
            forks = csv.DictReader(fcsv)
            for f in forks:
                try:
                    u = self.g.get_user(f['owner_username'])

                    #STEP 1: get user
                    if type(u) is not github.NamedUser.NamedUser:
                        print "ERROR: Cannot process ",f
                        continue

                    #STEP 2: get user_event_analysis for that user
                    self.events_analysis[u.login] = {}

                    uea = GitHubEventsInfo(u)

                    self.events_analysis[u.login]['commits_made'] = uea.get_commits_made()
                    self.events_analysis[u.login]['forks_created'] = uea.get_forks_created()
                    self.events_analysis[u.login]['pull_requests_made'] = uea.get_pull_requests_made()
                    self.events_analysis[u.login]['issues_created'] = uea.get_issues_created()
                    self.events_analysis[u.login]['issues_resolved'] = uea.get_issues_resolved()
                    self.events_analysis[u.login]['repositories_created'] = uea.get_repositories_created()
                except Exception as e:
                    print type(e)
                    print e

        #STEP 3: Serialize the user_events_analysis
        with open('user_events_analysis.json','a') as ueajson:
            import json
            json.dump(self.events_analysis, ueajson, indent=4)

            ueajson.flush()

if __name__ == "__main__":
    
    #Initiate API connection
    #specify a username and password to get over the rate limit of GitHub API
    gi = GithubInfo(
            login = settings.login,
            password = settings.password,
            user = settings.COURSE_REPO_OWNER, #Owner of the repo which is our research's starting point for analysis
            repo = settings.COURSE_REPO_NAME) #Name ofthe repo which is our research's starting point for analysis

    #gi.forks_info()
    #gi.commits_info()
    #gi.pull_request_info()
    #gi.store_all_user_events_info()
    #gi.get_all_user_event_aggregates()
    gi.store_all_user_events_analysis()
