import logging
logger = logging.getLogger()
x = logging.StreamHandler()
logger.addHandler(x)

from dateutil.parser import parse
from dateutil.tz import tzlocal, tzutc
from datetime import datetime

repos = {}
commits = {}
pull_requests = {}

def get_all_related_repos(r):
    'retrieves all forks and any forks of these forks and so on of a given repo'
    for r in r.get_forks():
        if r.owner.name is None: #Some users don't fill the name...apparently!
            repos[r.owner.login] = r
        else:
            repos[r.owner.name] = r

        if r.forks_count > 0:
            print "This has been further forked...printing them"
            get_all_related_repos(r)

    return repos

def get_all_commits_on_repos(repos):
    '''Expects `repos` to be a non-empty dictionary of owner:repo pairs'''
    for r in repos.values():
        cs = r.get_commits()
        for c in cs:
            if c.commit.last_modified is not None:
                date_ist = parse(c.commit.last_modified).astimezone(tzlocal()).ctime()
            else:
                date_ist = None

            commits[c.sha] = {'author':c.author.name, 'committer' : c.committer.name, 'repo': r.name, 'repo_url' : r.url, 'date':  date_ist, 'comment': c.commit.message}
            if c.author.name is None or c.author.name.strip() == '':
                commits[c.sha]['author'] = c.author.login

            if c.committer.name is None or c.committer.name.strip() == '':
                commits[c.sha]['committer'] = c.committer.login

    return commits

def get_all_pull_requests(r):
    '''Gets all pull requests for the repo r, regardless of whether they are open or closed'''
    
    for p in r.get_pulls(state='all'):
        created_at_ist = p.created_at.replace(tzinfo=tzutc()).astimezone(tzlocal()).ctime()
        if p.closed_at is not None:
            closed_at_ist = p.closed_at.replace(tzinfo=tzutc()).astimezone(tzlocal()).ctime()
        else:
            closed_at_ist = None

        pull_requests[p.id] = {'user': p.user.name, 'created_at': created_at_ist, 'closed_at': closed_at_ist, 'additions':p.additions, 'deletions':p.deletions, 'changed_files': p.changed_files, 'review_comments' : p.review_comments, 'merged' : p.is_merged()}

        if p.user.name is None or p.user.name.strip() == '':
            pull_requests[p.id]['user'] = p.user.login

    return pull_requests
