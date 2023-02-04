# python3 launch.py --restart
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import lxml
import urllib.robotparser
import word_processing as wp
import csv
import json

validLinkHistory = set()
totalLinkHistory = set()
robotHistory = dict()
websiteContentHistory = set()
wp.create_data_folder()

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    actualURL = resp.url
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    statusCode = resp.status
    # resp.error: when status is not 200, you can check the error here, if needed.
    if statusCode != 200:
        return []
    else:
        # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
        rawResponse = resp.raw_response
        #resp.raw_response.content: the content of the page!
        htmlContent = rawResponse.content
        soup = BeautifulSoup(htmlContent, "lxml")
        links = soup.find_all('a', href=True)
        
        alltext = soup.get_text()
        tokens = wp.tokenize(alltext)
        if len(tokens) < 100:
            return []
        frequencies = wp.compute_word_frequencies(tokens)
        pagelength = wp.compute_page_length(tokens)


        hashed = wp.compute_hash(tokens)
        if hashed in websiteContentHistory: #it is a duplicated website
            writeInvalid(7,url)
            return []
        else:
            websiteContentHistory.add(hashed)
            wp.write_csv(url,pagelength,hashed,json.dumps(frequencies))


        links = [i.get('href') for i in links]
        # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
        if links: return links
        return []


def determineNetLocValid(text):
    return re.search(
            r"ics.uci.edu|"
            + r"cs.uci.edu|"
            + r"informatics.uci.edu|"
            + r"stat.uci.edu", text.lower()
        )

def determinePathQueryInvalid(text):
    return re.match(
            r"(.*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            #program files, ends with
            + r"|scm|ss|py|java|r|c|m|odc|war" 
            #program files, ends with
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$)" 
            #bad, surrounded by anything
            + r"|(.*(action=login|action=edit|action=upload|action=download|action=source|"
            + r"action=lostpassword|share=|calendar|ical=[0-9]+|page\/[0-9]+).*)"
            #bad, surrounded by anything
            , text.lower())


def determineRobotValid(fullurl,parsed):
    robotURL = parsed.scheme + "://" + parsed.netloc + "/robots.txt"
    if getResponseCode(robotURL) != 200:
        return False
    if robotURL in robotHistory:
        return robotHistory[robotURL].can_fetch("IR UW23 55097037,94863973,34175030,70796407",fullurl)
        
    else:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robotURL)
        rp.read()
        robotHistory[robotURL] = rp
        return rp.can_fetch("IR UW23 55097037,94863973,34175030,70796407",fullurl)


def determineFragmentInvalid(text):
    return re.match(
            r".*(comment-|respond).*"
            , text.lower())

def getResponseCode(url):
    try:
        conn = urllib.request.urlopen(url)
        return conn.getcode()
    except:
        return -1

def writeInvalid(error,url):
    with open('data/invalid.txt',"a") as f:
        f.write(str(error)+"    "+url) 
        f.write("\n")

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        

        totalLinkHistory.add(url)
        if url in totalLinkHistory:
            # writeInvalid(5,url)
            return False
    
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            # writeInvalid(0,url)
            return False
        if getResponseCode(url) != 200:
            writeInvalid(1,url)
            return False

        if not determineNetLocValid(parsed.netloc):
            writeInvalid(2,url)
            return False

        if determinePathQueryInvalid(parsed.path):
            writeInvalid(3,url)
            return False

        if determinePathQueryInvalid(parsed.query):
            writeInvalid(4,url)
            return False

        if not determineRobotValid(url,parsed):
            writeInvalid(6,url)
            return False
        
        if determineFragmentInvalid(parsed.fragment):
            writeInvalid(8,url)
            return False

        validLinkHistory.add(url)  #add link to overall history
        with open('data/valid.txt',"a") as f:
            f.write(url) 
            f.write("\n")
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise

if __name__ == '__main__':
    print('reset data folder')