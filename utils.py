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


def add_days(number_day):
    if number_day == 1:
        day = 'день'
    elif int(str(number_day)[-1]) in [2, 3, 4]:
        day = 'дня'
    elif int(str(number_day)[-1]) in [5, 6, 7, 8, 9, 0]:
        day = 'дней'
    return str(number_day) + ' ' + day
