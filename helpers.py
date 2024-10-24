from tokenizer import *
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urldefrag
import re

unique_urls = set()
word_frequency = {}
longest_page_url = None
max_word_count = 0
subdomains = {}
stop_words = set()

# Data recording helper functions

def add_unique_url(url):
    global unique_urls

    # Removes fragment from url
    defrag_url, frag = urldefrag(url)

    # If the url has not been seen, add it to unique_urls
    if(defrag_url not in unique_urls):
        unique_urls.add(defrag_url)

def update_word_frequency(text, content):
    global word_frequency

    # Tokenizes the words and adds them to the valid_words list if it is not in stop_words
    words = tokenize(text) 
    valid_words = [word for word in words if word not in stop_words]
    
    # Records words to the overall word frequency dictionary
    word_frequency = compute_frequencies(valid_words, word_frequency)

def count_words_in_page(text, url):
    global longest_page_url, max_word_count

    # Counts the number of words on the page
    words = text.split()
    word_count = len(words)

    # Checks if the page has the most words and updates the word count and url if so
    if word_count > max_word_count:
        max_word_count = word_count
        longest_page_url = url

def track_subdomain(url):
    global subdomains

    parsed_url = urlparse(url)
    subdomain = parsed_url.netloc

    # Removes "www." if it exists 
    if subdomain.startswith("www."):
        subdomain = subdomain[4:]

    # Tracks subdomain frequency
    if subdomain not in subdomains:
        subdomains[subdomain] = 0
    subdomains[subdomain] += 1

def record_data(content, url):
    # Extracts text from resp.raw_response.content
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text()

    # Records data from given url and page text
    add_unique_url(url)
    update_word_frequency(text, url)
    count_words_in_page(text, url)
    track_subdomain(url)


# is_valid helper functions

def is_valid_domain(url):  
    allowed_domains = [
        "ics.uci.edu",
        "cs.uci.edu",
        "informatics.uci.edu",
        "stat.uci.edu",
        "today.uci.edu"
    ]
    parsed_url = urlparse(url)
    subdomain = parsed_url.netloc

    # Checks if the domain of the url is one we are supposed to crawl
    if subdomain.endswith("today.uci.edu"):
        if not parsed_url.path.startswith("/department/information_computer_sciences/"):
            return False
    if any(subdomain.endswith(domain) for domain in allowed_domains):
        return True
    
    return False

def is_new_url(url):
    global unique_urls

    # Removes fragment from url
    defrag_url, frag = urldefrag(url)

    if(defrag_url in unique_urls):
        return False
    else
        return True

def is_infinite_trap(url):
    # Detect URLs with the page pattern  like \page=1, \page=2, etc.
    has_page_pattern = re.search(r'[\?&]page=\d+', url)
    
    if has_page_pattern:
        return True
    return False



# Function to load stop words from a text file
def load_stop_words(path, words):
    with open(path, 'r') as file:
        for line in file:
            # Clears any whitespace and makes sure that the current line has a word before adding it
            word = line.strip()  
            if word:
                words.add(word.lower())

# Loads stop words from 'stopwords.txt'
load_stop_words("stopwords.txt", stop_words)