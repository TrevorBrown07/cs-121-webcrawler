import re
import sys
from bs4 import BeautifulSoup
import json

def tokenize(link_text):
    token_list = []
    ok_chars = r"[^A-Za-z0-9]" # Regular expression to only accept alphanumeric characters
    expression = re.compile(ok_chars)
    try:
        for line in file:
            fixed_line = expression.sub(' ', line) # Remove non alphanumeric characters from the line
            for token in fixed_line.split():
                token_list.append(token.lower())
    except:
        print(f"File Failed to Read {text_file_path}: File not text file")
        file.close()
        return []
    file.close() # Close file
    return token_list

def compute_word_frequencies(token_list):
    frequencies = {}
    for token in token_list:
        if token in frequencies: #Checks if the token is already in the dict, if is increments count, else adds token to dict
            frequencies[token] += 1
        else:
            frequencies[token] = 1
    return frequencies

def print_frequencies(frequencies):
    pair_list = [ (-frequencies[key], key) for key in frequencies] # list comprehension to create list of reversed tuples for each token, value is negative for proper sorting
    pair_list.sort() # Sorts the tuples in reverse order for their values and forward order for their keys
    for value, key in pair_list:
        print(f"<{key}> = <{-value}>")
