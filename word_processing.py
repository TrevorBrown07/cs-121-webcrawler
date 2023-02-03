import re
import json
import pathlib
from urllib.parse import urlparse
import hashlib
import csv
from collections import Counter
from collections import defaultdict
stop_list = set(['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an',
            'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before',
            'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could',
            "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down',
            'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't",
            'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's",
            'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've",
            'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't",
            'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours',
            'ourselves','out','over','own','same',"shan't",'she',"she'd","she'll","she's","should","shouldn't",'so','some',
            'such','than','that',"that's","the","their","theirs","them","themselves","then","there","there's",'these',
            'they',"they'd","they'll","they're","they've",'this','those','through','to','too','under','until','up','very',
            'was',"wasn't",'we',"we'd","we'll","we're","we've",'were',"weren't",'what',"what's",'when',"where's",'which',
            'while','who',"who's",'whom','why',"why's",'with',"won't",'would',"wouldn't",'you',"you'd","you'll","you're","you've",
            "your","yours",'yourself','yourselves'])

def tokenize(text):
    ALPHANUMERIC = r'\b([0-9a-zA-Z]+)\b'
    return [word.lower() for word in re.findall(ALPHANUMERIC,text)]

def compute_word_frequencies(token_list):
    frequencies = {}
    for token in token_list:
        if token in frequencies: #Checks if the token is already in the dict, if is increments count, else adds token to dict
            frequencies[token] += 1
        else:
            frequencies[token] = 1
    return frequencies

def compute_hash(token_list):
    string = ""
    for i in range(min(10,len(token_list))):
        string+= token_list[i]
    string+=str(len(token_list))
    return hashlib.md5(string.encode('utf-8')).hexdigest()

def create_data_folder():
    # Creates the data folder or overwrites it if it already exists
    pathlib.Path("data").mkdir(exist_ok = True)
    pathlib.Path("data/valid.txt").touch(exist_ok=True)
    with open('data/report.txt', 'w', newline='') as f:
        f.write("")
    pathlib.Path("data/testing.csv").touch(exist_ok=True)
    with open('data/testing.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Link", "Length", "Hash","Frequencies"])
    pathlib.Path("data/valid.txt").touch(exist_ok=True)
    with open('data/valid.txt', 'w', newline='') as f:
        f.write("")
    pathlib.Path("data/invalid.txt").touch(exist_ok=True)
    with open('data/invalid.txt', 'w', newline='') as f:
        f.write("")

def write_csv(first,second,third,fourth):
    with open('data/testing.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([first,second,third,fourth])


def compute_page_length(token_list):
    return len(token_list)

def find_longest_page():
    columns = defaultdict(list)
    with open("data/testing.csv","r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                if k == "Length":
                    columns[k].append(int(v))
                else:
                    columns[k].append(v)
                    
    maxIndex = columns["Length"].index(max(columns["Length"]))

    with open("data/report.txt", "a") as f:
        f.write(f"\nLongest page found: {columns['Link'][maxIndex]} {columns['Length'][maxIndex]} \n\n")


def tally_top_50_words():
    top50 = Counter()

    columns = defaultdict(list)
    with open("data/testing.csv","r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                if k == "Frequencies":
                    top50.update(Counter(json.loads(v)))

    answer = ""
    count = 0
    for i in top50.most_common():
        if i[0] not in stop_list and len(i[0]) != 1:
            answer += (str(i) + "\n")
            count += 1
        if count >= 50:
            break
    
    with open("data/report.txt", "a") as f:
        f.write(f"Top 50 words:\n{answer}\n")
    

def count_unique_links():
    totalLinks = set()
    columns = defaultdict(list)
    with open("data/testing.csv","r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                if k == "Link":
                    totalLinks.add(v.replace(urlparse(v).fragment,""))
    with open("data/report.txt", "a") as f:
        f.write(f"Total number of unique URLs: {len(totalLinks)}\n")
        for i,v in enumerate(totalLinks,1):
            f.write("["+str(i)+"] "+v)
            f.write("\n")

    
def count_subdomains():
    totalLinks = defaultdict(set)
    columns = defaultdict(list)
    with open("data/testing.csv","r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for (k,v) in row.items():
                parsed = urlparse(v)
                if k == "Link" and re.search(r"ics.uci.edu",parsed.netloc):
                    totalLinks[parsed.scheme+"://"+parsed.netloc].add(v.replace(parsed.fragment,""))
    answer = ""
    for i,v in totalLinks.items():
        answer += i + " "+str(len(v))+"\n"
        count = 1
        for j in v:
            answer += " ["+str(count)+"] "+j
            count += 1
        answer += "\n\n"
        
    with open("data/report.txt", "a") as f:
        f.write(f"Subdomains:{len(totalLinks)}\n{answer}\n\n")

def create_report():
    with open("data/report.txt", "w") as f:
        f.write("")
    count_unique_links()
    find_longest_page()
    tally_top_50_words()
    count_subdomains()

if __name__ == '__main__':
    create_report()