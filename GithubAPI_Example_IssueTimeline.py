import stscraper as scraper
import pandas as pd
import json
import os,time


class repoMethod(scraper.GitHubAPI):
    
    @scraper.api_filter(lambda issue: 'pull_request' not in issue)
    @scraper.api('repos/%s/issues', paginate=True, state='closed')
    def repo_closed_issues(self, repo_slug):
        """Get repository issues (not including pull requests)"""
        # https://developer.github.com/v3/issues/#list-issues-for-a-repository
        return repo_slug

    def repo_pulls_count(self, repo_slug,pull_state):
        """return the result of pull requests"""
        #https://developer.github.com/v3/pulls/#list-pull-requests
        url ='repos/'+repo_slug+'/pulls'
        repopulls= self.request(url, paginate=True,state=pull_state)
        return repopulls

    def repo_contributor_count(self, repo_slug):
        """return the result of pull requests"""
        #https://developer.github.com/v3/pulls/#list-pull-requests
        url ='repos/'+repo_slug+'/contributors'
        repocontr= self.request(url, paginate=True)
        return repocontr
    
    def repo_commits_count(self, repo_slug):
        """return the result of pull requests"""
        #https://developer.github.com/v3/pulls/#list-pull-requests
        url ='repos/'+repo_slug+'/commits'
        repocomts= self.request(url, paginate=True)
        return repocomts
    
    def repo_api_check(self, repo_slug):
        url='repos/'+repo_slug
        repoResponse=self.request(url,paginate=False)
        return repoResponse

    def search_closed_issues(self, repo_source_slug, repo_mentioned_slug):
        """ Return timeline on an issue or a pull request
                :param repo: str 'owner/repo'url
                :param issue_id: int, either an issue or a Pull Request id
                """
        # append to repos['items'] list
        # keep going through the results pages and extract ['items']
        # append extracted items to original
        q=repo_mentioned_slug+'+type:issues+state:closed+repo:'+repo_source_slug
        url = 'search/issues?q='+q
        repos = self.request(url, paginate=False)
        page = 1
        total_repos = min(repos['total_count'], 1000)
        items_remaining = total_repos - len(repos['items'])
        while items_remaining > 0:
            print("Repository search results remaining: {}".format(items_remaining))
            # next page
            page += 1
            url ='search/issues?q='+q+'&page='+str(page)
            repos['items'] += self.request(url, paginate=False)['items']
            items_remaining = total_repos - len(repos['items'])
        return repos



    #from https://github.com/shuiblue/GitHubAPI-Crawler by Prof.Shurui Zhou, for collecting issue/PR timelines
    def issue_pr_timeline(self, repo, issue_id):
        """ Return timeline on an issue or a pull request
        :param repo: str 'owner/repo'url
        :param issue_id: int, either an issue or a Pull Request id
        """
        url = "repos/%s/issues/%s/timeline" % (repo, issue_id)
        events = self.request(url, paginate=True, state='all')
        for event in events:
            # print('repo: ' + repo + ' issue: ' + str(issue_id) + ' event: ' + event['event'])
            if event['event'] == 'cross-referenced':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': "",
                    'created_at': event.get('created_at'),
                    'id': event['source']['issue']['number'],
                    'repo': event['source']['issue']['repository']['full_name'],
                    'type': 'pull_request' if 'pull_request' in event['source']['issue'].keys() else 'issue',
                    'state': event['source']['issue']['state'],
                    'assignees': event['source']['issue']['assignees'],
                    'label': "",
                    'body': ''
                }
            elif event['event'] == 'referenced':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': event['commit_id'],
                    'created_at': event['created_at'],
                    'id': '',
                    'repo': '',
                    'type': 'commit',
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            elif event['event'] == 'labeled':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': '',
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "label",
                    'state': '',
                    'assignees': '',
                    'label': event['label']['name'],
                    'body': ''
                }
            elif event['event'] == 'committed':
                yield {
                    'event': event['event'],
                    'author': event['author']['name'],
                    'email': event['author']['email'],
                    'author_type': '',
                    'author_association': '',
                    'commit_id': event['sha'],
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "commit",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            elif event['event'] == 'reviewed':
                author = event['user'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': event['author_association'],
                    'commit_id': '',
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "review",
                    'state': event['state'],
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            elif event['event'] == 'commented':
                yield {
                    'event': event['event'],
                    'author': event['user']['login'],
                    'email': '',
                    'author_type': event['user']['type'],
                    'author_association': event['author_association'],
                    'commit_id': '',
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "comment",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': event['body']
                }
            elif event['event'] == 'assigned':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': '',
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "comment",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            elif event['event'] == 'closed':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': event['commit_id'],
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "close",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            elif event['event'] == 'subscribed':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': event['commit_id'],
                    'created_at': event.get('created_at'),
                    'id': event['commit_id'],
                    'repo': '',
                    'type': "subscribed",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            elif event['event'] == 'merged':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': event['commit_id'],
                    'created_at': event.get('created_at'),
                    'id': event['commit_id'],
                    'repo': '',
                    'type': "merged",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            elif event['event'] == 'mentioned':
                author = event['actor'] or {}
                yield {
                    'event': event['event'],
                    'author': author.get('login'),
                    'email': '',
                    'author_type': author.get('type'),
                    'author_association': '',
                    'commit_id': '',
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "mentioned",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }
            else:
                yield {
                    'event': event['event'],
                    'author': '',
                    'email': '',
                    'author_type': '',
                    'author_association': '',
                    'commit_id': '',
                    'created_at': event.get('created_at'),
                    'id': '',
                    'repo': '',
                    'type': "",
                    'state': '',
                    'assignees': '',
                    'label': '',
                    'body': ''
                }



def read_json_df(filename):
    jsonfile=open(filename,encoding="utf-8")
    obj=jsonfile.read()
    commitsJson=json.loads(obj)
    jsondf=pd.DataFrame(commitsJson)
    jsonfile.close()

    return jsondf

def read_excel_df(filename):
    df = pd.read_excel(filename,sheet_name=0)
    df=pd.DataFrame(df)
    return df


def read_keywords_list(path):
    with open(path) as wordfile:
        keywords_list = wordfile.read().splitlines()
    wordfile.close()

    return keywords_list

def get_timeline_repo(filepath,reposlug):
    indexOverall=0

    # for example, a json file storing all the repo slugs and the issue ids("issue_number") of the repo,
    jsonpath="Example.json"
    repodf=read_json_df(jsonpath)

    currentrepo_timeline_dfs=[]


    for i in range(repodf.shape[0]):
        start_time=time.time()
        print(indexOverall)
        current_issue_number=repodf.iloc[i]['issue_number']

        current_timeline=gh_api.issue_pr_timeline(reposlug,int(current_issue_number))
        timeline_df=pd.DataFrame(current_timeline)
        timeline_df["repo_source"]=reposlug
        timeline_df["issue_number"]=current_issue_number
        timeline_df["issue_status"]="closed"
        currentrepo_timeline_dfs.append(timeline_df)
        indexOverall+=1
        end_time=time.time()
        times=round(end_time-start_time,2)
        print('total scraping time is{}s'.format(times))
        print(indexOverall)

    mergeddf=pd.concat(currentrepo_timeline_dfs,ignore_index=True)
    mergeddf.to_excel(filepath+"file.xls")



#main 
if __name__ == '__main__':

    savefilepath="D:\\"

    # Your github tokens for using GithubAPI
    gh_api =repoMethod("token1,token2,token3,token4,token5")


    # the list of repo slugs that you have already collected issues for. You can store the issues collected along with their repo slug into a json file.
    repo_list=read_keywords_list('D:\\repolist.txt')
    
    for i in range(len(repo_list)):
        get_timeline_repo(savefilepath,repo_list[i])
