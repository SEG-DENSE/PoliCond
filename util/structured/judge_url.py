import re
from typing import Union


def is_valid_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^(https?://)?(www\.)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$'
    )
    return bool(url_pattern.match(url))


def find_url(text: str) -> Union[str, None]:
    url_pattern = re.compile(
        r'(?P<url>https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
    )
    match = url_pattern.search(text)
    return match.group("url") if match else None


def has_url(text: str) -> bool:
    return find_url(text) is not None


def test1():
    test_urls = [
        "http://example.com",
        "https://www.example.com/path",
        "ftp://example.com",  # Invalid for this pattern
        "www.example.com",
        "example.com",
        "http://-example.com",
        "http://", # False
        "This is a sentence without a proper noun.",
        "The capital of the U.S.A. is Washington, D.C.",
        "Contact us at NASA for more information.",
        "Alice",
        "Bob Smith",
        "john",
        "U.S.A.",
        "NASA",
        "this is not a proper noun"
    ]

    for url in test_urls:
        print(f"{url}: Is valid URL? {is_valid_url(url)}")

def test2():
    test_texts = [
        "Visit us at http://example.com for more information.",
        "This is an invalid URL: ftp://example.com",
        "Check www.example.com for details.",
        "No URL here!",
        "This is a sentence without a proper noun.",
        "The capital of the U.S.A. is Washington, D.C.",
        "Contact us at NASA for more information.",
        "Alice",
        "Bob Smith",
        "john",
        "U.S.A.",
        "NASA",
        "this is not a proper noun",
    ]

    for text in test_texts:
        print(f"Searching in: '{text}'")
        res=find_url(text)
        if res:
            print("URL:", res,"; for text.txt:",text)
        else:
            print(f"No {text}")

if __name__ == '__main__':
    test1()
    test2()
