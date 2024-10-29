import re
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from helpers import *



def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    


#Checks if content has headers and then if the content is actually text/html, and not pdf, etc.
    try:
        if(resp.raw_response and hasattr(resp.raw_response, 'headers')):
            ConType = resp.raw_response.headers.get("Content-Type")
            if (ConType and "text/html" not in ConType):
                
                if (EnableCountPrints): #TURN TRUE AT THE TOP OF HELPERS.py IF YOU WANT TO SEE BUGFIXING PRINTS
                    print(f"bad type: {ConType}")
                    print(f"Missing Header: {hasattr(resp.raw_response, 'headers')}; and Raw Response: {resp.raw_response}; and Code: {resp.status}; and Type: {ConType}")
                return []
        else:
            if (EnableCountPrints): #TURN TRUE AT THE TOP OF HELPERS.py IF YOU WANT TO SEE BUGFIXING PRINTS
                print(f"Missing Header: {hasattr(resp.raw_response, 'headers')}; and Raw Response: {resp.raw_response}; and Code: {resp.status};")

            return []
    except:
        return []
    # if(not has_high_text_content(resp.raw_response)):
    #     print("Low textual content.")
    #     return []

    
#This is the actual extraction of URLs
    URList = []  #This holds all the valid URLs to be returned

    if (resp.status == 200):
        #This is when we get a valid page to parse and analize

        content = resp.raw_response.content

        if(not has_high_text_content(content)):
            if (EnableCountPrints): #TURN TRUE AT THE TOP OF HELPERS.py IF YOU WANT TO SEE BUGFIXING PRINTS
                print("Low textual content.")

            return []

        record_data(content, url) #updates our final report stats
        
        try:
            decoded_content = content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(decoded_content, "lxml") #This parses our HTML content and enables useful methods like below
            text = soup.find_all('a')  #Finds all anchors<a> in soup, which typically holds urls. Returns a List of Soup objects, each represent something in the content, hopefully a URL. . .                    
            
            for urls in text: 

                if (is_valid(urls.get("href"))):  #call is_Valid on every URL by getting the URL directly from the soup object
                    if(add_unique_url(urls.get("href"))):  #Checks if unqiue URL
                        URList.append(urls.get("href")) #If it is valid, add it to URList

        except Exception as msg:
            print(f"Something happened: {msg}") 
            
            
    
        #I was just curious how many urls per url
        # print(f"Number of links: {len(text)}")
        # print(f"Number of valid links: {len(URList)}")
            

       

    else:
        print(f"This is not a valid page: {url}; Gave Code: {resp.status}; Gave Error: {resp.error}") #bugfixing

    return URList


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        url = unquote(url)
    except:
        return False

    if url is None:     #First off, it cant be None, which is possible for some reason.
        # print("URL is None")
        return False 
    
    
    if (not is_valid_domain(url)): #call helper which filters for required UCI websites
        return False
    
    if(is_Filter(url)):
        return False
    
    if (is_iCalendar(url)):
        return False

    if (is_infinite_trap(url)):
        return False

    if (check_calendar_trap(url)):
        return False
    
    try:
        parsed = urlparse(url)


        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower() + parsed.query.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
