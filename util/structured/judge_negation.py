import re
from typing import Union

# a set of words related to "negation"
negations = {
    "not", "no", "never", "none", "nothing", "nowhere", "neither", "nobody",
    "no one", "will not", "can't", "cannot", "doesn't", "don't", "isn't", "aren't",
    "wasn't", "weren't", "haven't", "hasn't", "hadn't", "hardly", "scarcely", "barely",
    "didn't", "won't", "wouldn't", "does not","do not","is not","are not","was not",
    "should not","shall not","ain't","ain’t", "nor", "seldom","little","few","rare"
}


# whether a word is a valid negation
def is_negation(input: str) -> bool:
    return input.lower() in negations

# find all negation words in the text
def find_all_negation(text: str) -> Union[list[str], None]:
    words = re.findall(r'\b\w+\b', text.lower())  
    negations_found = [word for word in words if is_negation(word)] 

    if negations_found:
        return negations_found
    return None

# check if the text contains any negation word
def has_negation(text: str) -> bool:
    return find_all_negation(text) is not None

# test1: to check api is_negation
def test1():
    test_inputs = [
        "no",
        "yes",
        "never",
        "always",
        "nothing",
        "everything",
        "maybe"
    ]

    for noun in test_inputs:
        print(f"{noun}: Is negation? {is_negation(noun)}")

# test2: to check if the text contains negation words
def test2():
    test_texts = [
        "Alice went to the market.",
        "He did not go to the market.",
        "There is no way to fix this.",
        "She is always late.",
        "I don't know the answer."
    ]

    for text in test_texts:
        print(f"Text: '{text}'")
        print(f"Has negation? {has_negation(text)}")
        print(f"Negations found: {find_all_negation(text)}\n")

if __name__ == '__main__':
    test1()
    test2()
