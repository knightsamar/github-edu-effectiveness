from github import Github
from utils import get_all_related_repos, get_all_commits_on_repos, get_all_pull_requests
import csv

class GithubInfo:
    r = None
    repos = {}
    commits = {}
    pull_requests = {}

    def __init__(self, user = 'gayatrivenugopal', repo = "MobileTechnologies"):
        self.r = g.get_user(user).get_repo(repo)

    def forks_info(self):
        self.repos = get_all_related_repos(self.r)
        with open('forks.csv','w') as fcsv:
            fieldnames = ['owner', 'repo']
            w = csv.DictWriter(fcsv, fieldnames)

            w.writeheader()
            for o,r in self.repos.items():
                w.writerow({'owner':o, 'repo':r.name})

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

if __name__ == "__main__":
    
    #Initiate API connection
    g = Github(login_or_token=None,password=None) #Use your username and password for getting over rate limit.
    
    gi = GithubInfo(user='gayatrivenugopal', repo='MobileTechnologies') #Initate our Info gatherer

    gi.forks_info()
    gi.commits_info()
    gi.pull_request_info()
