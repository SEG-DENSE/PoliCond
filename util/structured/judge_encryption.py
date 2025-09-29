import re
import base64


def is_possible_encrypt(s: str) -> bool:
    return s and len(s) > 4 and (is_blake2s(s) or is_base64(s) or is_sha256(s))


def is_sha256(s):
    sha256_pattern = re.compile(r'^[0-9a-fA-F]{64}$')
    return bool(sha256_pattern.match(s))


def is_base64(s: str) -> bool:
    if not s:
        return False

    padding = len(s) % 4
    if padding not in [0, 2]:
        return False

    try:
        base64.b64decode(s, validate=True)
        return True
    except Exception:
        return False


def is_blake2s(s):
    blake2s_pattern = re.compile(r'^[0-9a-fA-F]{64}$')
    return bool(blake2s_pattern.match(s))


def test():
    test_strings = [
        "a7f8c3d4e2b9186e4d1c2b4567890abcdefa7f8c3d4e2b9186e4d1c2b4567890",  # Blake2s 
        "SGVsbG8gd29ybGQ=",  # Base64 encoded "Hello world"
        "invalid string",  # illegal string
        '00aa288de1e6ce28d4b1447b879eb1238ebc76b4ff6d81eee19ee404d5717899'  # Blake2s
    ]

    for s in test_strings:
        print(f"{s}:")
        print("  Is SHA-256:", is_sha256(s))
        print("  Is Base64:", is_base64(s))
        print("  Is Blake2s:", is_blake2s(s))
        print()


if __name__ == '__main__':
    test()
