import requests
import os
import time
import re
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
        Return: a 3D dict [x][y][z] where:
            x is a keyword
            y is a url of a post found to contain keyword x
            dict[x][y] contains a breakdown of components of a given post:
                title: the title of the post
                url: the url of the post
                comments: the url to the comments section of the post
                comment_count: the total number of comments

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
                url = p.select_one('[data-testid="outbound-link"]')['href']

                if url is None:
                    url = "https://reddit.com" + p.select_one('[data-click-id="body"]')['href']

                results[t][url] = {"title": title}
                results[t][url]["url"] = url
                count = p.select_one('[data-click-id="comments"] span').text
                c_power = count.split()[0]

                if 'k' in c_power:
                    c_power = 3.0
                elif 'm' in c_power:
                    c_power = 6.0
                else:
                    c_power = 0.0

                count = re.sub('[^0-9.]', '', count)

                if c_power > 0.0:
                    results[t][url]["comment_count"] = int(float(count) * (10.0 ** c_power))
                else:
                    results[t][url]["comment_count"] = int(count)

                results[t][url]["comments"] = p.select_one('[data-test-id="comments-page-link-num-comments"]')['href']

                break
    return results

if __name__ == "__main__":
    sample_site = "manga"
    sample_targets = ["Good Morning", "Please Go Home", "Jujutsu Kaisen", "Ganbare", "Dandadan", "RuriDragon", "One Punch Man", "Getting more and more"]
    r = reddit_search(sample_site, ["news"])

    print("--- Results ---")
    for k in r.keys():
        print("-" + k)
        for p in r[k].keys():
            print("----------")
            for i in r[k][p].keys():
                print("\t" + i + " : " + r[k][p][i])
