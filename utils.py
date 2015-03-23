import json
import requests
users = []

class GitHub:
    users = []  #users that we are concerned with.
    repos = {}  #repos that we are concerned with, including forks
    commits = [] #all commits that we are concerned with

    def get_forks(self, url):
        fs = requests.get(url)
        fs_json = json.loads(fs.text or fs.content)

        for f in fs_json:
            print "Owner: ", f['owner']['login']
            login = f['owner']['login']
            self.users.append(login)
            print "Fork : ", f['name'], f['url']
            self.repos[login] = f['name']
            if f['forks_count'] > 0:
                print "This has been further forked...printing them"
                self.get_forks(f['forks_url'])

    def commits_on_repos(self, repos):
        '''Expects `repos` to be a non-empty dictionary of owner:repo pairs'''
        import pdb
        pdb.set_trace()
        for owner,repo in repos.items():
            repo_url = "https://api.github.com/repos/%s/%s/commits" % (owner, repo)
            commits = json.loads(requests.get(repo_url).text)
            
            for c in commits:
                print c['commit']['tree']['sha']
    
    def get_commits_by_users(self, users):
        '''Expects `users` to be a non-empty list of string login names.'''
        #TODO: List all commits done by a user on ALL repos.
