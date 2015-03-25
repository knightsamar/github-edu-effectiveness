import logging
logger = logging.getLogger()
x = logging.StreamHandler()
logger.addHandler(x)

repos = {}
commits = {}
pull_requests = {}

def get_all_related_repos(r):
    'retrieves all forks and any forks of these forks and so on of a given repo'
    for r in r.get_forks():
       repos[r.owner.name] = r #record

       if r.forks_count > 0:
           print "This has been further forked...printing them"
           get_all_related_repos(r)

    return repos

def get_all_commits_on_repos(repos):
    '''Expects `repos` to be a non-empty dictionary of owner:repo pairs'''
    for r in repos.values():
        cs = r.get_commits()
        for c in cs:
            print "c", c
            commits[c.sha] = {'author':c.author.name, 'committer' : c.committer.name, 'repo': r.name, 'repo_url' : r.url, 'date': c.commit.last_modified, 'comment': c.commit.message}
            if c.author.name is None or c.author.name.strip() == '':
                commits[c.sha]['author'] = c.author.login

            if c.committer.name is None or c.committer.name.strip() == '':
                commits[c.sha]['committer'] = c.committer.login

    return commits

def get_all_pull_requests(r):
    '''Gets all pull requests for the repo r, regardless of whether they are open or closed'''
    
    for p in r.get_pulls(state='all'):
        pull_requests[p.id] = {'user': p.user.name, 'created_at': p.created_at, 'closed_at':p.closed_at, 'additions':p.additions, 'deletions':p.deletions, 'changed_files': p.changed_files, 'review_comments' : p.review_comments, 'merged' : p.is_merged()}

        if p.user.name is None or p.user.name.strip() == '':
            pull_requests[p.id]['user'] = p.user.login

    return pull_requests
