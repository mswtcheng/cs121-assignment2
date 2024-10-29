from tokenizer import *
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urldefrag
from datetime import datetime, timedelta
import re
import pickle

unique_urls = set()
word_frequency = {}
longest_page_url = None
max_word_count = 0
subdomains = {}
stop_words = set()
calendar_date_dict = {}  # Stores dates per base URL

last_save_time = datetime.now()
last_log_time = datetime.now()
calendarDates = []

EnableCountPrints = True #TURN TRUE IF YOU WANT TO SEE BUGFIXING PRINTS, THERES ANOTHER ONE YOU NEED TO BE TRUE FOR SCRAPER


def log_stats(): #This is not complete, simply prints stats for now, intend to make it write to file, also need to figure when to call this, every hour, every sec, etc??
    with open("Logged_Stats.txt", 'a') as file:

        file.write(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        
        file.write(f"Unique Urls Amount: {len(unique_urls)}\n\n")
        
        file.write(f"Longest Page is {max_word_count}: {longest_page_url}\n\n")
        
        file.write(f"50 Most Common Words: {len(word_frequency)}\n")
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
    global last_save_time
    # Extracts text from resp.raw_response.content
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text()


    # if(len(unique_urls)%100 ==0):  #this logs stats every time number of unique values is 
    #     if (EnableCountPrints): #TURN TRUE AT THE TOP IF YOU WANT TO SEE BUGFIXING PRINTS
    #         print(len(unique_urls))

    #     log_stats()
    #     print("LOGGED STATS!!!")


    # Records data from given url and page text
    # add_unique_url(url)
    update_word_frequency(text, url)
    count_words_in_page(text, url)
    track_subdomain(url)
    
    current_time = datetime.now()
    if current_time - last_save_time >= timedelta(seconds=20):  #saves every 20 sec
        save_stats()
        print("_____________SAVED STATS_____________")
        print(len(unique_urls))
        
        last_save_time = current_time  # Update the last save time

    if current_time - last_log_time >= timedelta(seconds=300): #log every 5 min
        log_stats()
        if (EnableCountPrints): #TURN TRUE AT THE TOP IF YOU WANT TO SEE BUGFIXING PRINTS
            print(len(unique_urls))
            print("_____________LOGGED STATS_____________")
        last_log_time = current_time  # Update the last save time


# is_valid helper functions

def is_iCalendar(url):
    # Check if the URL contains the substring "?outlook"
    if "?outlook" in url or "ical" in url:
        return True  # Return False if the substring is found
    return False 

def is_Filter(url):
    # Check if the URL contains the substring "?filter" or "&filter"
    if "?filter" in url or "&filter" in url:
        return True  # Return False if the substring is found
    return False 

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
    if any(subdomain == domain or subdomain.endswith("." + domain) for domain in allowed_domains):
        return True
    
    return False


def is_infinite_trap(url):
    # Detect URLs with the page pattern  like \page=1, \page=2, etc.
    has_page_pattern = re.search(r'[\?&]page=\d+', url)
    #has_page_pattern = re.search(r'page', url)
    
    if has_page_pattern:
        return True
    return False

# def check_calendar_trap(url):
#     # check if "eventDate=" is in URL (common search pattern)
#     if "eventDate=" in url:
#         # get the substring following "eventDate="
#         date_str = url.split("eventDate=")[-1][:10]
#         try:
#             # validate date format
#             event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
#             # add unique dates to calendarDates
#             if event_date not in calendarDates:
#                 calendarDates.append(event_date)
            
#             # Check if a calendar trap is detected by finding sequential dates
#             if len(calendarDates) >= 15 and check_for_sequential_dates(calendarDates):
#                 return True  # Indicate a calendar trap detected
#         except ValueError:
#             # If the date format is incorrect, pass
#             pass
#     return False  # No trap detected

def check_calendar_trap(url):
    # Extract the base URL (netloc)
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.netloc}"
    # Check for date patterns in the URL
    date_match = re.search(r'[/\?&=](\d{4}[-/]\d{1,2}[-/]\d{1,2})', url)
    if(not date_match):
        date_match = re.search(r'[/\?&=](\d{4}[-/]\d{1,2})', url)

    if date_match:
        date_str = date_match.group(1)
        try:
            # validate date format
            if len(date_str) == 10:  # 'YYYY-MM-DD'
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            elif len(date_str) == 7:  # 'YYYY-MM'
                event_date = datetime.strptime(date_str, "%Y-%m").date()

            # Initialize date list for new base URLs
            if base_url not in calendar_date_dict:
                calendar_date_dict[base_url] = set()
            
            # add unique dates to base URL's date list
            calendar_date_dict[base_url].add(event_date)

            # Check if a calendar trap is detected by finding any 10 dates
            if len(calendar_date_dict[base_url]) >= 10: 
                return True
        except ValueError:
            pass

    return False

def check_for_sequential_dates(dates):
    # Sort dates and check for consecutive daily differences
    sorted_dates = sorted(dates)
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i - 1]).days != 1:
            return False  # dates are not in sequential daily order
    return True  # all dates are sequential


def has_high_text_content(content):
    # Extracts text from the page and counts the words
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text()
    word_count = len(text.split())
    
    # Calculates text-HTML ratio of the page
    text_length = len(text)
    html_length = len(content)

    if (text_length == 0 or html_length == 0):
        return False
    
    if (EnableCountPrints): #TURN TRUE AT THE TOP IF YOU WANT TO SEE BUGFIXING PRINTS
        print(f"ratio: {text_length / html_length}")
        print(f"text: {text_length}")
        print(f"html: {html_length}")
        print(f"word count: {word_count}")
        links = soup.find_all('a')  #Finds all anchors<a> in soup, which typically holds urls. Returns a List of Soup objects, each represent something in the content, hopefully a URL. . .                    
        print(f"Number of URLS: {len(links)}")

    if html_length > 0:
        text_ratio = text_length / html_length 
    else:
        return False
    
    # Determines if page meets high-content criteria
    if (word_count >= 100 or text_ratio >= 0.08) and (text_ratio < 0.8) and (word_count > 40):
        return True
    return False



def save_stats():
    try:
        with open('crawler_stats.pkl', 'wb') as file:
            pickle.dump({
                'unique_urls': unique_urls,
                'word_frequency': word_frequency,
                'longest_page_url': longest_page_url,
                'max_word_count': max_word_count,
                'subdomains': subdomains,
                'calendar_date_dict': calendar_date_dict
            }, file)
    except Exception as e:
        print(f"Error saving stats: {e}")

def load_stats():
    global unique_urls, word_frequency, longest_page_url, max_word_count
    global subdomains, calendar_date_dict
    
    try:
        with open('crawler_stats.pkl', 'rb') as file:
            stats = pickle.load(file)
            unique_urls = stats['unique_urls']
            word_frequency = stats['word_frequency']
            longest_page_url = stats['longest_page_url']
            max_word_count = stats['max_word_count']
            subdomains = stats['subdomains']
            calendar_date_dict = stats['calendar_date_dict']
    except (FileNotFoundError, EOFError):
        print("No previous stats found, starting fresh.")



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
load_stats()

#print Current Stats to show updating
print("CURRENTSTATS")
print(f"#UniqueURls: {len(unique_urls)}")
print(f"#WordFrequency: {len(word_frequency)}")
print(f"LongestPage: {longest_page_url}")
print(f"LongestPageWordCount: {max_word_count}")
print(f"#Subdomains: {len(subdomains)}")
print(f"#CalendarDict: {len(calendar_date_dict)}")