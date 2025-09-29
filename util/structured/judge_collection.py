import re
from typing import Union

# a set of words related to "collect"
collections = {
    "collect", "gather", "use","share","offer","assemble", "accumulate", "aggregate", "amass", "harvest",
    "gather up", "bring together", "compile", "round up", "pick up", "consolidate",
    "hoard", "stockpile", "scoop up", "pile up", "collect up", "accumulate",
    "store", "save", "recoup", "assemble together", "bring in", "draw together",
    "take in", "capture", "collate",
    "collection", "collectible", "collector", "collecting", "collected", "collective",
    "accumulation", "aggregator", "gathering", "amassment", "hoarding", "stockpiling",
    "compilation", "roundup", "harvested", "collation","give","request","ask","receive",
    "send","provide","grant"
    "contribute","present","supply","yield","lend","afford",
    "grant","contribute","present","supply","yield","lend"
}

# whether a word is related to "collect"
def is_collection(input: str) -> bool:
    return input.lower() in collections

# find all words related to "collect" in the text
def find_all_collection(text: str) -> Union[list[str], None]:
    # using regex to find all words in the text
    words = re.findall(r'\b\w+\b', text.lower()) 
    collections_found = [word for word in words if is_collection(word)]

    if collections_found:
        return collections_found 
    return None

# check if the text contains any word related to "collect"
def has_collection(text: str) -> bool:
    return find_all_collection(text) is not None

# test case
def test1():
    print(len(collections))
    test_texts = [
        "Alice is collecting data from the users.",
        "The project involves gathering information.",
        "They are accumulating resources for the event.",
        "She is not interested in collecting stamps.",
        "This book is not related to collection at all.",
        "We gather and accumulate data regularly."
    ]

    for text in test_texts:
        print(f"Text: '{text}'")
        print(f"Has collection-related word? {has_collection(text)}")
        print(f"Collection-related words found: {find_all_collection(text)}\n")

if __name__ == '__main__':
    test1()
