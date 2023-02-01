import re
import json
import pathlib

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
    ok_chars = r"[^A-Za-z0-9]" # Regular expression to only accept alphanumeric characters
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
    pathlib.Path("data/report.txt").touch(exist_ok=True)
    pathlib.Path("data/valid.txt").touch(exist_ok=True)

def save_word_count(frequencies):
    file = open("data/word_counts.txt", "a")
    json.dump(frequencies, file)
    file.write("\n")
    file.close()

def tally_top_50_words():
    word_counts_file = open("data/word_counts.txt", "r")
    output_file = open("data/report.txt", "a")
    output_file.write("Top 50 Words in the domains: \n")
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
            output_file.write(f"{count}: Word: <{key}> Total: <{-value}> \n")
            count += 1
    output_file.write("\n")
    word_counts_file.close()
    output_file.close()

def count_unique_links():
    url_file = open("data/valid.txt", 'r')
    url_count_file = open("data/report.txt", "a")
    url_count = 0
    for line in url_file:
        url_count += 1
    url_count_file.write(f"Total number of unique URLs: {url_count} \n\n")
    url_file.close()
    url_count_file.close()
    

def count_subdomains():
    pass
    
    
