import re


def clear_html(text):
    return re.sub(r'\<[^>]*\>', '', text)


def send_sms(text):
    print('\nSend SMS:', text)


def clear(item):
    for el in [".", ",", "!", "?", ":", ";"]:
        item = item.replace(el, "")
    return item


def print_(name, text):
    print(f"{name}:", text) if text else None
