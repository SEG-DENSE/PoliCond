import re
from typing import Union

# proper_noun_pattern = re.compile(r'^(?:[A-Z][a-zA-Z0-9]*(?:[\s_-][A-Z][a-zA-Z0-9]*)*|[A-Z]+)$')
# more precise, lower recall
proper_ptn1 = r'^[A-Z][A-Za-z]*(?:[\s_-·.][A-Z]*)*$'
proper_ptn2 = r'^[A-Z][A-Za-z]*(?:[\s_-·.][A-Z]*)*$'


def is_valid_proper_noun(noun: str) -> bool:
    proper_noun_pattern = re.compile(proper_ptn1)
    return bool(proper_noun_pattern.match(noun))


def find_proper_noun(text: str) -> Union[str, None]:
    proper_noun_pattern = re.compile(proper_ptn2)
    match = proper_noun_pattern.search(text)
    return match.group(0) if match else None


def has_proper_noun(text: str) -> bool:
    return find_proper_noun(text) is not None


def test1():
    test_nouns = [
        "Alice",
        "Bob Smith",
        "john",  # Invalid
        "U.S.A.",
        "NASA",
        "this is not a proper noun",
        "Hao123",  # True
        "K12 Inc",
        "Google",
        "this is a sentence",
        "This is a sentence"
    ]

    for noun in test_nouns:
        print(f"{noun}: Is valid proper noun? {is_valid_proper_noun(noun)}")


def test2():
    test_texts = [
        "Alice went to the market.",
        "This is a sentence without a proper noun.",
        "The capital of the U.S.A. is Washington, D.C.",
        "Contact us at NASA for more information.",
        "Alice",
        "Bob Smith",
        "john",
        "U.S.A.",
        "NASA",
        "this is not a proper noun",
        "Hao123",
        "K12 Inc",
        "Google",
        "this is a sentence",
        "This is a sentence"
        "This is a sentence"
        "Fare Company a sentence"
        "This is a sentence,"
        "This is a sentence, OK?"
    ]

    for text in test_texts:
        res = find_proper_noun(text)
        if res:
            print(f"Found proper noun:{res} for {text}")
        else:
            print(f"No for {text}")


if __name__ == '__main__':
    # test1()
    test2()
