import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    #print(corpus)
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    result = {}
    if len(corpus[page])==0:
        #print (page,{i:(1/len(corpus)) for i in corpus.keys()})
        return {i:(1/len(corpus)) for i in corpus.keys()}

    z = lambda x: 1 if x in corpus[page] else 0
    for i in corpus.keys():
        result[i]=(1-damping_factor)/len(corpus) + damping_factor*z(i)/len(corpus[page])
    #print(page, result)
    return result
    #raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PageRank = transition_model(corpus, random.choice(list(corpus.keys())), damping_factor)
    for i in range(0, n-1):
        k=[]
        v=[]
        for i in PageRank.keys():
            k.append(i)
            v.append(PageRank[i])
        transition=transition_model(corpus, random.choices(k, v, k=1)[0], damping_factor)
        for i in PageRank.keys():
            PageRank[i] = (PageRank[i]+transition[i])
    for i in PageRank.keys():
            PageRank[i] = PageRank[i]/n
    return PageRank
    raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    result = {i:(1/len(corpus)) for i in corpus.keys()}
    new_result = {}

    for i in corpus.keys():
        new_result[i] = float((1-damping_factor)/len(corpus)) 
        for j in corpus.keys():
            if i in corpus[j]:
                new_result[i] += float(damping_factor*result[j]/len(corpus[j]))

    while (True):
        if not(any([abs(result[i] - new_result[i])>0.001 for i in corpus.keys()])):
            break
        result = copy.deepcopy(new_result)

        for i in corpus.keys():    
            new_result[i] = float((1-damping_factor)/len(corpus)) 
            for j in corpus.keys():
                if i in corpus[j]:
                    new_result[i] += float(damping_factor*result[j]/len(corpus[j]))

    #normalisation                
    sum = 0
    for i in corpus.keys():
        sum+=new_result[i]
    for i in corpus.keys():
        new_result[i]/=sum

    return new_result

    raise NotImplementedError


if __name__ == "__main__":
    main()
