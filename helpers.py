from tokenizer import *
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urldefrag
import datetime
import re

unique_urls = set()
word_frequency = {}
longest_page_url = None
max_word_count = 0
subdomains = {}
stop_words = set()
url_count_map = {}

def log_stats(): #This is not complete, simply prints stats for now, intend to make it write to file, also need to figure when to call this, every hour, every sec, etc??
    with open("Logged_Stats.txt", 'a') as file:

        file.write(f'Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        
        file.write(f"Unique Urls Amount: {len(unique_urls)}\n\n")
        
        file.write(f"Longest Page: {longest_page_url}\n\n")
        
        file.write("50 Most Common Words:\n")
        for key, value in sorted(word_frequency.items(), key=lambda item: item[1], reverse=True)[:50]:  #Prints top 50 words in terms of frequency
            file.write(f"{key}: {value}\n")
        
        file.write("\n")

        file.write("Subdomains:\n")
        for key in sorted(subdomains):   #Prints subdomains in alphabetical order
            file.write(f"{key}, {subdomains[key]}\n")

        file.write("\n" + "="*40 + "\n\n")

# Data recording helper functions

def add_unique_url(url):
    global unique_urls

    # Removes fragment from url
    defrag_url, frag = urldefrag(url)

    # If the url has not been seen, add it to unique_urls
    if(defrag_url not in unique_urls):
        unique_urls.add(defrag_url)
        return True  
    else:
        return False    
    

def update_word_frequency(text, content):
    global word_frequency

    # Tokenizes the words and adds them to the valid_words list if it is not in stop_words
    words = tokenize(text) 
    valid_words = [word for word in words if word not in stop_words and len(word) > 1]
    
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


    if(len(unique_urls)%100 ==0):  #this logs stats every time number of unqiue values is 
        print(len(unique_urls))
        log_stats()


    # Records data from given url and page text
    # add_unique_url(url)
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


def is_infinite_trap(url):
    # Detect URLs with the page pattern  like \page=1, \page=2, etc.
    #has_page_pattern = re.search(r'[\?&]page=\d+', url)
    has_page_pattern = re.search(r'page', url)
    
    if has_page_pattern:
        return True
    return False

def has_high_text_content(content):
    # Extracts text from the page and counts the words
    text = BeautifulSoup(content, "lxml")
    word_count = len(text.split())
    
    # Calculates text-HTML ratio of the page
    text_length = len(text)
    html_length = len(html_content)
    if html_length > 0 
        text_ratio = text_length / html_length 
    else
        return False
    
    # Determines if page meets high-content criteria
    if word_count >= 100 and text_ratio >= 0.05:
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