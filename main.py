from utils import GitHub

#forks of https://api.github.com/repos/gayatrivenugopal/MT_A_Feedback
g = GitHub()
g.get_forks("https://api.github.com/repos/gayatrivenugopal/MT_A_Feedback/forks")
print g.repos

g.commits_on_repos(g.repos)
        
