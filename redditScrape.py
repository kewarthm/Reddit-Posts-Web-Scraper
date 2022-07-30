import requests
import os
import time
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
fileDir = os.path.dirname(os.path.realpath('__file__'))
path = os.path.join(fileDir, "chromedriver.exe")

def reddit_search(subreddit, targets):
    '''
        (str, [str]) -> {str : {str : str}}
        Takes a subreddit name and a list of keywords. Using Selenium and Beautiful soup
        all recent posts with titles containing a keyword will be returned.

        subreddit: the name of the target subreddit
        targets: a list of keywords to look for in posts
        Return: a 2D dict [x][y] where:
            x is a keyword
            y is a title of a post found to contain keyword x
            dict[x][y] contains the link to the post

    '''
    if not (type(subreddit) == str):
        raise TypeError("subreddit must be a string")
    if not (type(targets) == list):
        raise TypeError("Keywords must be a list")
    for k in targets:
        if not (type(k) == str):
            raise TypeError("A keyword is not a string")
    results = {}
    for t in targets:
        results[t] = {}

    driver = webdriver.Chrome(options=options, executable_path = path)
    driver.get("https://www.reddit.com/r/" + subreddit)
    driver.implicitly_wait(220)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight,)")
    page = driver.page_source
    driver.close()

    soup = BeautifulSoup(page, "html.parser")
    posts = soup.select('[data-testid="post-container"]')

    if not posts:
        raise Exception("Subreddit does not exist")

    for p in posts:
        title = p.select_one('h3').text
        for t in targets:
            if t.lower() in title.lower():
                if p.select_one('figure') is not None:
                    #post has an in-laid image(s), save href to post
                    results[t][title] = "https://reddit.com" + p.select_one('[data-click-id="body"]')['href']

                elif p.select_one('[data-click-id="media"]') is not None:
                    results[t][title] = "https://reddit.com" + p.select_one('[data-click-id="body"]')['href']

                elif p.select_one('[data-click-id="background"]') is not None:
                    results[t][title] = "https://reddit.com" + p.select_one('[data-click-id="body"]')['href']

                else:
                    results[t][title] = p.select_one('[data-testid="outbound-link"]')['href']

                break
    return results

if __name__ == "__main__":
    sample_site = "manga"
    sample_targets = ["Good Morning", "Please Go Home", "Jujutsu Kaisen", "Ganbare", "Dandadan", "RuriDragon", "One Punch Man", "Getting more and more"]
    r = reddit_search(sample_site, sample_targets)

    print("--- Results ---")
    for k in r.keys():
        print("-" + k)
        for p in r[k].keys():
            print("\t" + p + " : " + r[k][p])
