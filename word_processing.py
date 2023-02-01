import re
import json
import pathlib
from urllib.parse import urlparse

stop_list = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an',
            'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before',
            'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could',
            "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down',
            'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't",
            'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's",
            'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've",
            'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't",
            'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours']

def tokenize(link_text):
    token_list = []
    ok_chars = r"[^A-Za-z0-9']" # Regular expression to only accept alphanumeric characters
    expression = re.compile(ok_chars)
    fixed_text = expression.sub(' ', link_text) # Remove non alphanumeric characters from the text
    for token in fixed_text.split():
        token_list.append(token.lower())
    return token_list

def compute_word_frequencies(token_list):
    frequencies = {}
    for token in token_list:
        if token in frequencies: #Checks if the token is already in the dict, if is increments count, else adds token to dict
            frequencies[token] += 1
        else:
            frequencies[token] = 1
    return frequencies

def create_data_folder():
    # Creates the data folder or overwrites it if it already exists
    pathlib.Path("data").mkdir(exist_ok = True)
    pathlib.Path("data/word_counts.txt").touch(exist_ok=True)
    pathlib.Path("data/page_lengths.txt").touch(exist_ok=True)
    pathlib.Path("data/report.txt").touch(exist_ok=True)
    pathlib.Path("data/valid.txt").touch(exist_ok=True)
    pathlib.Path("data/invalid.txt").touch(exist_ok=True)

def compute_page_length(token_list):
    return len(token_list)

def save_page_length(page_lengths):
    file = open("data/page_lengths.txt", "a")
    json.dump(page_lengths)
    file.write("\n")
    file.close()

def find_longest_page():
    page_lengths_file = open("data/page_lengths.txt", "r")
    report = open("data/report.txt", "a")
    current_longest = ("placeholder", 0)
    for line in page_lengths_file:
        pl_pair = json.loads(line)
        for key in pl_pair:
            if pl_pair[key] > current_longest[1]:
                current_longest = (key, pl_pair[key])
    report.write(f"Longest Page by number of words: {current_longest} \n\n")
    page_lengths_file.close()
    report.close()

def save_word_count(frequencies):
    file = open("data/word_counts.txt", "a")
    json.dump(frequencies, file)
    file.write("\n")
    file.close()

def tally_top_50_words():
    word_counts_file = open("data/word_counts.txt", "r")
    report = open("data/report.txt", "a")
    report.write("Top 50 Words in the domains: \n")
    freq_totals = {}
    for line in word_counts_file:
        freq = json.loads(line)
        for key in freq:
            if key in freq_totals:
                freq_totals[key] += freq[key]
            else:
                freq_totals[key] = freq[key]
    # list comprehension to create list of reversed tuples for each token, value is negative for proper sorting
    pair_list = [ (-freq_totals[key], key) for key in freq_totals] 
    pair_list.sort()
    count = 1
    for value, key in pair_list:
        if count > 50:
            break
        if key in stop_list:
            pass
        else:
            report.write(f"{count}: Word: <{key}> Total: <{-value}> \n")
            count += 1
    report.write("\n")
    word_counts_file.close()
    report.close()

def count_unique_links():
    url_file = open("data/valid.txt", 'r')
    report = open("data/report.txt", "a")
    url_count = 0
    for line in url_file:
        url_count += 1
    report.write(f"Total number of unique URLs: {url_count} \n\n")
    url_file.close()
    report.close()
    
def count_subdomains():
    url_file = open("data/valid.txt", 'r')
    report = open("data/report.txt", "a")
    subdomains = {"ics.uci.edu": 0}
    for line in url_file:
        url = urlparse(line)
        domain = re.sub("^www.", "", url.netloc)
        if domain in subdomains:
            subdomains[domain] += 1
        elif(re.match(".+\.ics.uci.edu$", domain)):
            subdomains[domain] = 1
    report.write("ics.uci.edu subdomains: \n")
    for domain in subdomains:
        report.write(f"{domain}, {subdomains[domain]}\n")
    report.write("\n")
    url_file.close()
    report.close()

def create_report():
    count_unique_links()
    find_longest_page()
    tally_top_50_words()
    count_subdomains()

if __name__ == '__main__':
    create_report()
