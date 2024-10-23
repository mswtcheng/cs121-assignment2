from tokenizer import *
from bs4 import BeautifulSoup

word_frequency = {}
stop_words = set()
longest_page_url = None
max_word_count = 0

def update_word_frequency(content):
    global word_frequency
    
    # Extract text from resp.raw_response.content
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text()

    # Tokenizes the words
    words = tokenize(text) 
    valid_words = [word for word in words if word not in stop_words]
    
    # Records words to the overall word frequency dictionary
    word_frequency = compute_frequencies(valid_words, word_frequency)

def count_words_in_page(content, url):
    global longest_page_url, max_word_count
    
    # Extracts text from resp.raw_response.content
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text()

    # Counts the number of words on the page
    words = text.split()
    word_count = len(words)

    # Checks if the page has the most words and updates the word count and url if so
    if word_count > max_word_count:
        max_word_count = word_count
        longest_page_url = url

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