from store import connect
from github import Github
from settings import COURSE_REPO, COURSE_REPO_NAME

class GitHubEventsInfo(object):
    username = None
    commits_made = None
    pull_requests_made = None
    forks_created = None
    issues_created = None
    issues_resolved = None

    def __init__(self, username):
        try:
            u = Github().get_user(username)
            if u is not None:
                self.username = username
            else:
                return False
        except Exception as e:
            print e

    def get_commits_made(self):
        #TODO: Further filter the commits on other repos based on date.

        '''
        Gives back:
        
        number of commits made on the course repo
        number of commits made on the course repo's fork
        number of commits made on other repos before the course started
        number of commits made on other repos after the course ended

        '''
        db = connect()
        on_course_repo = db.events.find({
            'actor.login'  : self.username,
            'repo.name'    : COURSE_REPO,
            'type'         : 'PushEvent',
        })

        on_course_repo_fork = db.events.find({
            'actor.login'  : self.username,
            'repo.name'    : '%s/%s' % (self.username, COURSE_REPO_NAME),
            'type'         : 'PushEvent',
        })

        on_other_repos = db.events.find({
            'actor.login'  : self.username,
            'repo.name'    : {'$nin' : [COURSE_REPO, '%s/%s' % (self.username, COURSE_REPO_NAME)]},
            'type'         : 'PushEvent',
        })
        
        self.commits_made = {}

        self.commits_made['on_course_repo'] = {
                'push'     : on_course_repo.count(), #total pushes
                'commit'   : sum([push['payload']['size'] for push in on_course_repo],0), #sum total of commits in each push
                'repo'      : on_course_repo.distinct('repo.name')
                }

        self.commits_made['on_course_repo_fork'] = {
                'push'     : on_course_repo_fork.count(),
                'commit'   : sum([push['payload']['size'] for push in on_course_repo_fork],0),
                'repo'      : on_course_repo_fork.distinct('repo.name'),
                }

        self.commits_made['on_other_repos'] = {
                'push'     : on_other_repos.count(),
                'commit'   : sum([push['payload']['size'] for push in on_other_repos],0),
                'repo'     : on_other_repos.distinct('repo.name'),
                }

        return self.commits_made

    def get_pull_requests_made(self):
        #TODO: Further filter the pull requests on other repos based on date.

        '''
        Gives back:
        
        number of pull requests made on the course repo
        number of pull requests made on the course repo's fork
        number of pull requests made on other repos before the course started
        number of pull requests made on other repos after the course ended

        '''
        db = connect()
        on_course_repo = db.events.find({
            'actor.login'  : self.username,
            'repo.name'    : COURSE_REPO, #TODO: Figure out why repo.full_name doesn't work here!
            'type'         : 'PullRequestEvent',
        })
        
        on_other_repos = db.events.find({
            'actor.login'  : self.username,
            'repo.name'    : {'$nin' : [COURSE_REPO, '%s/%s' % (self.username, COURSE_REPO_NAME)]},
            'type'         : 'PullRequestEvent',
        })
        
        self.pull_requests_made = {}

        self.pull_requests_made['on_course_repo'] = {
                'count'      : on_course_repo.count(), #total pull requests
                'repo'       : on_course_repo.distinct('repo.name')

                }

        self.pull_requests_made['on_other_repos'] = {
                'count'    : on_other_repos.count(),
                'repo'     : on_other_repos.distinct('repo.name'),
                }

        return self.pull_requests_made

    def get_forks_created(self):
        #TODO: Further filter the commits on other repos based on date.
        '''
        get the details of any forks that were created by the user of

        the course repo
        other repos before the course started
        other repos after the course ended
        '''
        #TODO: GET AND STORE all get_forks() data for all users in a forks collection in MongoDB and use it here.
        db = connect()
        of_course_repo = db.events.find({
            'actor.login'   : self.username,
            'repo.name'     : COURSE_REPO,
            'type'          : 'ForkEvent',
        })

        of_other_repos = db.events.find({
            'actor.login'      : self.username,
            'repo.name'        : {'$ne' : COURSE_REPO},
            'type'             : 'ForkEvent',
        })


        self.forks_created = {}

        self.forks_created['of_course_repo'] = {
                'count'      : of_course_repo.count(), #total forks created -- I know this weird but it is 0400 hrs and I hv more imp things in code to worry about
                'fork_of'    : of_course_repo.distinct('repo.name')
                }

        self.forks_created['of_other_repos'] = {
                'count'      : of_other_repos.count(), #total forks created 
                'fork_of'    : of_other_repos.distinct('repo.name')
                }

        return self.forks_created

    def get_issues_created(self):
        '''
        Gets the details of any issues OPENED or REOPENED by the user on

        1. the course repo
        2. fork of the course repo
        3. other repos before the course started
        4. other repos after the course ended
        '''
        #TODO: Further filter the issues based on date as required by 3) and 4) above
        db = connect()

        #get data
        on_course_repo = db.events.find({
            'actor.login'   : self.username,
            'repo.name'     : COURSE_REPO,
            'type'          : 'IssuesEvent',
            'payload.action': { '$in' : ['opened','reopened']},
            })

        on_course_repo_fork = db.events.find({
            'actor.login'   : self.username,
            'repo.name'     : '%s/%s' % (self.username, COURSE_REPO_NAME),
            'type'          : 'IssuesEvent',
            'payload.action': { '$in' : ['opened','reopened']},
            })

        on_other_repos = db.events.find({
            'actor.login'   : self.username,
            'repo.name'     : {'$nin' : [COURSE_REPO, '%s/%s' % (self.username, COURSE_REPO_NAME)]},
            'type'          : 'IssuesEvent',
            'payload.action': { '$in' : ['opened','reopened']},
            })

        #store the data
        self.issues_created = {}

        self.issues_created['on_course_repo'] = {
            'count'         : on_course_repo.count(),
            'repos'         : on_course_repo.distinct('repo.name'),
            }

        self.issues_created['on_course_repo_fork'] = {
            'count'         : on_course_repo_fork.count(),
            'repos'         : on_course_repo_fork.distinct('repo.name'),
            }

        self.issues_created['on_other_repos'] = {
            'count'         : on_other_repos.count(),
            'repos'         : on_other_repos.distinct('repo.name'),
            }

        return self.issues_created

    def get_issues_resolved(self):
        '''
        Gets the details of any issues CLOSED by the user on

        1. the course repo
        2. fork of the course repo
        3. other repos before the course started
        4. other repos after the course ended
        '''
        #TODO: Further filter the issues based on date as required by 3) and 4) above
        db = connect()

        #get data
        on_course_repo = db.events.find({
            'actor.login'   : self.username,
            'repo.name'     : COURSE_REPO,
            'type'          : 'IssuesEvent',
            'payload.action': 'closed',
            })

        on_course_repo_fork = db.events.find({
            'actor.login'   : self.username,
            'repo.name'     : '%s/%s' % (self.username, COURSE_REPO_NAME),
            'type'          : 'IssuesEvent',
            'payload.action': 'closed',
            })

        on_other_repos = db.events.find({
            'actor.login'   : self.username,
            'repo.name'     : {'$nin' : [COURSE_REPO, '%s/%s' % (self.username, COURSE_REPO_NAME)]},
            'type'          : 'IssuesEvent',
            'payload.action': 'closed',
            })

        #store the data
        self.issues_resolved = {}

        self.issues_resolved['on_course_repo'] = {
            'count'         : on_course_repo.count(),
            'repos'         : on_course_repo.distinct('repo.name'),
            }

        self.issues_resolved['on_course_repo_fork'] = {
            'count'         : on_course_repo_fork.count(),
            'repos'         : on_course_repo_fork.distinct('repo.name'),
            }

        self.issues_resolved['on_other_repos'] = {
            'count'         : on_other_repos.count(),
            'repos'         : on_other_repos.distinct('repo.name'),
            }

        return self.issues_resolved