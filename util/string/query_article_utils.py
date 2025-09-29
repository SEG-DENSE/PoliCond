import re
from collections import Counter
from typing import Union, List

from util.string.preprocess import preprocess_string


def get_relevant_paras(query: Union[str, List[str]], article: str) -> str:
    if isinstance(query, list):
        query = ' '.join(query)  

    # split
    sentences = re.split(r'(?<=[.!?])\s+', article)

    # to save the most relevant sentence
    most_relevant_sentence = ""
    highest_score = 0

    # transform query to lower case and split into words
    query_words = query.lower().split()
    query_word_count = Counter(query_words)

    for sentence in sentences:
        sentence = sentence.lower()
        words_in_sentence = sentence.split()

        # get the count of matching words
        match_count = sum((word in words_in_sentence) for word in query_word_count)

        # if the match count is higher than the current highest score, update
        if match_count > highest_score:
            highest_score = match_count
            most_relevant_sentence = sentence

    return most_relevant_sentence


def clean_and_query(query:  Union[str, List[str]], article: str) -> str:
    if isinstance(query, list):
        query = ' '.join(query)  
    _article = preprocess_string(article)
    _query = preprocess_string(query)

    return get_relevant_paras(_query, _article)


if __name__ == '__main__':
    # example
    article = "This is an example ARTICLE with multiple paragraphs. Each paragraph contains different information that might be relevant to a given query."
    query = "example"
    res1 = get_relevant_paras(query, article)
    print(res1)
    res2 = clean_and_query(query, article)
    print(res2)

    query2=["example","contains","with","different","relevant"]
    res3 = get_relevant_paras(query2, article)
    print(res3)
    res4 = clean_and_query(query2, article)
    print(res4)