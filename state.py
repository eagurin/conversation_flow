# from __future__ import annotations

# import asyncio
# import sys
# from abc import ABC, abstractmethod


# class Context:
#     _call_counter = 0
#     _state_counter = 0

#     def __init__(self, state, user, invoker, phrase, recognize, post):
#         self._user = user
#         self._invoker = invoker
#         self._recognize = recognize
#         self._phrase = phrase
#         self._post = post
#         self.last_state = state
#         self.transition_to(state)

#     def transition_to(self, state):
#         print("\nState:", type(state).__name__)
#         self._state = state
#         self._state.user = self._user
#         self._state.post = self._post
#         self._state.recognize = self._recognize
#         self._state.entity = self._recognize.entity
#         self._state.intent = self._recognize.intent
#         self._state.product = self._recognize.product
#         self._state.phrase = self._phrase
#         self._state.push = self._phrase.push
#         self._state.say = self._phrase.say
#         self._state.listen = self._phrase.listen
#         self._state.say_and_listen = self._phrase.say_and_listen
#         self._state.result = self.result
#         self._state.request = self.request
#         self._state.hangup = self.hangup
#         self._state.transition_to = self.transition_to
#         self._state.context = self

#     def request(self):
#         self.counter()
#         self._state.question()
#         self._state.navigation()
#         self._state.basic()
#         self._state.handle()
#         self._phrase.say_and_listen('tail')
#         self.request()

#     def hangup(self):
#         print('\nЗвонок завершен.\n')
#         sys.exit()

#     def state_name(self):
#         return type(self._state).__name__

#     def result(self, text):
#         self._result = text
#         print("\nResult:", text)

#     def counter(self):
#         self._call_counter += 1
#         self._state_counter += 1
#         if self._state != self.last_state:
#             self._state_counter = 1
#         if self._call_counter > 50:
#             self._phrase.say('Что-то мы с вами заговорились!', 'А время- деньги!!')
#             self.hangup()
#         if self._state_counter > 10:
#             self._phrase.say('Хватит морочить мне голову!')
#             self.hangup()


# # class State(ABC):
# #     @property
# #     def context(self) -> Context:
# #         return self._context

# #     @context.setter
# #     def context(self, context: Context) -> None:
# #         self._context = context

#     # @property
#     # def user(self) -> Context:
#     #     return self._data

#     # @user.setter
#     # def user(self, data: Context) -> None:
#     #     self._data = data

#     # @property
#     # def recognize(self) -> Context:
#     #     return self._recognize

#     # @recognize.setter
#     # def recognize(self, recognize: Context) -> None:
#     #     self._recognize = recognize

#     # @property
#     # def phrase(self) -> Context:
#     #     return self._phrase

#     # @phrase.setter
#     # def phrase(self, phrase: Context) -> None:
#     #     self._phrase = phrase

#     # @abstractmethod
#     # def handle(self) -> None:
#     #     pass
