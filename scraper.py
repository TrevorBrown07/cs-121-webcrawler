import re
from urllib.parse import urlparse
import re
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import lxml
import word_processing


word_processing.create_data_folder()
validLinkHistoryNoFragments = set()
validLinkHistory = set()
totalLinkHistory = set()

def scraper(url, resp):
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    statusCode = resp.status
    # resp.error: when status is not 200, you can check the error here, if needed.
    if statusCode != 200:
        return []
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    rawResponse = resp.raw_response
    #resp.raw_response.content: the content of the page!
    htmlContent = rawResponse.content
    soup = BeautifulSoup(htmlContent, "lxml")
    token_list = word_processing.tokenize(soup.get_text()) #Create token list of text
    if not token_list: #If the token list is empty, page is dead, no need to continue
        return []
    parsed = urlparse(url)
    noFragment = url.replace(parsed.fragment,"")
    if noFragment in validLinkHistoryNoFragments: 
        pass
    else:
        validLinkHistoryNoFragments.add(noFragment) 
        with open('data/valid.txt',"a") as f:
            f.write(noFragment)
            f.write("\n")
        word_frequencies = word_processing.compute_word_frequencies(token_list)
        page_length = word_processing.compute_page_length(token_list)
        word_processing.save_page_length({url:page_length})
        word_processing.save_word_count(word_frequencies)
    links = extract_next_links(soup, resp)
    
    return [link for link in links if is_valid(link)]

def extract_next_links(soup, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    links = soup.find_all('a', href=True)
    links = [i.get('href') for i in links]
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if links:
        return links
    return []
    #resp.raw_response.url: the url, again

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        netlocValid = re.search(
            r"ics.uci.edu|"
            + r"cs.uci.edu|"
            + r"informatics.uci.edu|"
            + r"stat.uci.edu", parsed.netloc.lower()
        )
        pathValid = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

        queryValid = not re.match(
            r"(.*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|scm|ss|py|java|r|c|m|odc|war" #adscmsourcecode, sstemplatelanguage,odcmicrosoftdata,warwebsitefiles
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$)" #added 2 parentheses
            + r"|(.*(action=login|action=edit|action=upload|action=download|action=source|action=lostpassword))"

            
            
            , parsed.query.lower())
        
        duplicated = url in totalLinkHistory #returns true if url has not been seen

        everythingValid = netlocValid and pathValid and queryValid and not duplicated

        if (everythingValid): #netloc is correct, path is correct, and entire link is unique
            robotsTxt = RobotFileParser(parsed.scheme + "://" + parsed.netloc + "/robots.txt")
            robotsTxt.read()
            if not robotsTxt.can_fetch("UW23 55097037,94863973,34175030,70796407", url): # Check if url is allowed in robots.txt
                return False
            validLinkHistory.add(url)  #add link to overall history
            totalLinkHistory.add(url)
        else: #not valid
            with open('data/invalid.txt',"a") as f:
                if not duplicated and url not in validLinkHistory: #will only add links invalid because of structure, not dupes
                    f.write(url)
                    f.write("\n")
                    


        return everythingValid  #true if both true

    except TypeError:
        print ("TypeError for ", parsed)
        raise

if __name__ == '__main__':
    print('not this one')
