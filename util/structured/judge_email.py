import re
from typing import Union


def has_valid_email(email: str) -> bool:
    email_pattern = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    return bool(email_pattern.match(email))

def find_email(text: str) -> Union[str,None]:
    email_pattern = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )
    match = email_pattern.search(text)
    return match.group(0) if match else None

def is_valid_email(email: str) -> bool:
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(email_pattern.match(email))


def test_is_valid_email():
    test_emails = [
        "test@example.com",
        "invalid-email@",
        "user.name+tag+sorting@example.com",
        "user@subdomain.example.com",
        "user@.com",
        "user@domain..com",
        "107342r@qq.com",
        "dfg 107342r@qq.com 45345",
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

    for email in test_emails:
        print(f"{email}: Is valid email? {is_valid_email(email)}")

def test_find_email():
    test_texts = [
        "Contact us at support@example.com for assistance.",
        "This is an invalid email: user@.com",
        "Reach out to me at john.doe@example.co.uk!",
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
        res= find_email(text)
        if res:
            print("Found email:", res)


if __name__ == '__main__':
    test_is_valid_email()
    test_find_email()
