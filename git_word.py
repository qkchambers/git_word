#!/usr/bin/python3

import argparse
import pdb
import requests
import sys
from bs4 import BeautifulSoup

exclude = ["javascript:void(0);", ""]
url = None

# Prints out the urls
def print_urls(urls):
    for i in urls:
        print(i)

# Takes a list of urls and returns all the urls found through them
def crawl_urls(urls):
    crawled_urls = set()
    for url in urls:
        crawled_urls.add(get_urls(url))

    return crawled_urls

# Takes a url and returns the urls found through it
def get_urls(url):
    urls = set()
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml");

    for link in soup.find_all('a', attrs={'class':'js-navigation-open'}):

        # Remove uneeded class matches and parent directory
        if len(link.get("class")) < 2 and not link.get("rel"):
            fnd_url = link.get('href')
            if fnd_url not in exclude:
                urls.add(fnd_url)

    return urls


# Recursively travels into each directory and grabs the file/dir names
def clean_urls(paths, cur_dir):
    words = set()
    dirs = set()
    for path in paths:
        # blob correlates to a file
        parts = path.split("master")
        if len(parts) < 2:
            continue
        word = parts[1]
        if "blob" in path:
            words.add(word)

        # tree correlates to a path
        elif "tree" in path:
            dirs.add(word)

    # Grab urls from the directories
    for d in dirs:
        ps = get_urls(url+"/tree/master"+ d)
        print(url+"/tree/master"+d)
        ws = clean_urls(ps, d)
        for w in ws:
            words.add(w)

    return sorted(list(words))

# Writes urls to file
def save_words(filename, urls):
    with open(filename, 'w') as fo:
        fo.write("\n".join(urls))

# Handles errors for command line arguments
def parser_error(errmsg):
    print("Usage: python3 " + sys.argv[0] + " [Options] use -h for help")
    print(R + "Error: " + errmsg + W)
    sys.exit()

# Parse the arguments
def init_parser():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython3 ' + sys.argv[0] + " -w https://github.com/qkchambers/git_word")
    parser.error = parser_error
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-w', '--word', help="Creates a wordlist from the\
                        passed in git repository. The file is named after\
                        the repo.")
    return parser


def main():
    parser = init_parser()
    args = parser.parse_args()

    if args.word:
        # Create filename based on repo name
        url = args.word
        parts = url.split('/')
        filename = parts[len(parts)-1]+".txt"

        # Get urls, remove some and write to file
        paths = get_urls(url)
        words = clean_urls(paths, "")
        save_words(filename, words)

if __name__=="__main__":
    main()
