import re


def remove_html_tag(text: str) -> str:
    text = re.sub('<.*?>', '', text)
    text = re.sub(r'\|\|\|', '', text)
    text = re.sub(r"\n+", "\n", text)
    return text


if __name__ == '__main__':
    path = r'.\test\20_theatlantic.com.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        print(len(content))
        after_remove = remove_html_tag(content)
        print(len((remove_html_tag(content))))
