import re
import sys

# class Save:

#     def save_form_field(self) -> None:
#         self.set_name()
#         self.set_order_id()
    
#     def set_name(self):
#         if user.firstname:
#             self.name = user.firstname
#         if recognize.name:
#             self.name = recognize.name

#     def set_order_id(self):
#         if recognize.digit:
#             self.order_id = recognize.digit[0]


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
