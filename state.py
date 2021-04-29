from __future__ import annotations

import sys
from abc import ABC, abstractmethod


class Context:
    _result = None
    _hangup = None

    def __init__(self, state, user, invoker, phrase, recognize):
        self._user = user
        self._invoker = invoker
        self._recognize = recognize
        self._phrase = phrase
        self.transition_to(state)

    def transition_to(self, state: State):
        print("\nState:", type(state).__name__)
        self._state = state
        self._state.user = self._user
        self._state.r = self._recognize
        self._state.entity = self._recognize.entity
        self._state.intent = self._recognize.intent
        self._state.product = self._recognize.product
        self._state.phrase = self._phrase
        self._state.push = self._phrase.push
        self._state.say = self._phrase.say
        self._state.listen = self._phrase.listen
        self._state.say_and_listen = self._phrase.say_and_listen
        self._state.result = self.result
        self._state.request = self.request
        self._state.transition_to = self.transition_to
        self._state.context = self

    def request(self):
        if self._hangup:
            print('\nЗвонок завершен.\n')
            sys.exit()
        self._state.handle()

    def result(self, text):
        self._result = text
        print("\nResult:", text)


class State(ABC):
    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context

    @property
    def user(self) -> Context:
        return self._data

    @user.setter
    def user(self, data: Context) -> None:
        self._data = data

    @property
    def r(self) -> Context:
        return self._r

    @r.setter
    def r(self, recognize: Context) -> None:
        self._r = recognize

    @property
    def phrase(self) -> Context:
        return self._phrase

    @phrase.setter
    def phrase(self, phrase: Context) -> None:
        self._phrase = phrase

    @abstractmethod
    def handle(self) -> None:
        pass
