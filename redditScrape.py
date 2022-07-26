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
site = "https://www.reddit.com/r/manga"
target = ["Good Morning", "Please Go Home", "Jujutsu Kaisen", "Ganbare", "Dandadan", "RuriDragon", "One Punch Man", "Getting less and less tsun"]


def manga_search(site, targets):
    driver = webdriver.Chrome(options=options, executable_path = path)
    driver.get(site)
    driver.implicitly_wait(220)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight,)")
    page = driver.page_source
    driver.close()
    soup = BeautifulSoup(page, "html.parser")
    posts = soup.select('[data-testid="post-container"]')
    res = []
    link_res = []
    for p in posts:
        title = p.select_one('h3').text
        for t in targets:
            if t.lower() in title.lower():
                if p.select_one('figure') is not None:
                    #post has an in-laid image(s), save href to post
                    res.append(title)
                    link_res.append("https://reddit.com" + p.select_one('[data-click-id="body"]')['href'])

                elif p.select_one('[data-click-id="media"]') is not None:
                    res.append(title)
                    link_res.append("https://reddit.com" + p.select_one('[data-click-id="body"]')['href'])

                else:
                    res.append(title)
                    link_res.append(p.select_one('[data-testid="outbound-link"]')['href'])
                break
    return [res, link_res]

if __name__ == "__main__":
    r = manga_search(site, target)

    print("--- Results ---")
    for i in range(len(r)):
        print(r[0][i])
        print(r[1][i])

"""
    TODO:
        - need Selenium python module to decode dynamic webpage (reddit)
        - Complete parser -> parse through posts only
        - Compile results
        - email results to target email
        - convert project to module
        - post to git
"""
