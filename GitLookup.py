#!/usr/bin/env python3

from ghapi.all import GhApi, paged
from tabulate import tabulate as tab
import urllib.request, json 
import sys
# TODO: P0: use ghapi
# TODO: P0: use django
# TODO: P1: add include_forks Bool param
# TODO: P2: retrieve all pages in parallel
# TODO: P2: rightfetching (overfetching avoidance)
# TODO: P2: write Dockerfile

# if = true f = true => true
# if = true f = false => true
# if = false f = true => false
# if = false f = false => true

def main():
    include_forks = False
    if len(sys.argv)>0:
        if '--include_forks' in sys.argv:
            include_forks=True
    print ("provide the username:")
    username = input()
    api = GhApi()
    gen = paged(api.repos.list_for_user, username)
    rows = []
    totalStars=0
    lanbytes = {}
    try:
        for page in gen:
            try:
                for repo in page:
                    stargazers = repo.stargazers_count
                    fname = repo.name
                    totalStars+=stargazers
                    try:
                        with urllib.request.urlopen(repo.languages_url) as url:
                            data = json.loads(url.read().decode())
                            for key,val in data.items():
                                if not key in lanbytes:
                                    lanbytes[key]=0
                                lanbytes[key]+=val
                    except urllib.error.HTTPError as exception:
                        print("could not check languages for the repository %s:"%repo.name)
                        #match exception.code:
                            #case 401:
                            #    print("Authentication required\n")
                            #case 403:
                            #    print("Access denied\n")
                            #case 404 | 410:
                            #    print("Resource not found\n")
                            #case 500:
                            #    print("Internal server error\n")
                            #case _:
                            #    print(exception.message)
                        print("http error code:%d\n"%(exception.code))
                    except:
                        print("unknown problem has occured while checking languages for the repository %s"%repo.name)
                    if include_forks:
                        fork = '%s'%repo.fork if include_forks else '' 
                        rows.append([fname,stargazers,fork])
                    else:
                        if repo.fork:
                            continue
                        rows.append([fname,stargazers])
            except urllib.error.HTTPError as exception:
                print("could not load a repository")
    except urllib.error.HTTPError as exception:
        print("could not load a page")
    if include_forks:
        print(tab(rows,headers=['Name','Stars','Fork?'],tablefmt='orgtbl'))
    else:
        print(tab(rows,headers=['Name','Stars'],tablefmt='orgtbl'))
    print('%s has %d total stars'%(username,totalStars))
    print(lanbytes)
    mostPopularLanguage= max(lanbytes, key=lanbytes.get)
    print('most-used language - %s; bytes - %d'%(mostPopularLanguage,lanbytes[mostPopularLanguage]))

main()