from random import randint
from time import sleep


class PromptStack:
    _on_speak = None
    _on_listen = None
    _history = []
    _phrase = ''
    last = ''
    _ssml = ''

    def __init__(self, invoker, recognize, prompts_dict) -> None:
        self._invoker = invoker
        self._recognize = recognize
        self.PROMPTS = prompts_dict

    def push(self, *actions) -> None:
        self.add_history(*actions)
        for self.action in actions:
            self.check_in_prompts()
            self.add_in_phrase()

    def add_history(self, *actions):
        self._history.append(actions)

    def check_in_prompts(self) -> None:
        if self.action in self.PROMPTS:
            prompt_list = self.PROMPTS[self.action]
            self.action = prompt_list[randint(0, len(prompt_list)-1)]

    def add_in_phrase(self) -> None:
        self._phrase += str(self.action or ' ') + '<break time="250ms"/> '

    def say(self, *actions) -> None:
        self.push(*actions)
        self._invoker.set_on_speak(self._phrase)
        self._invoker.do_speak()
        self.last = self._phrase
        self._phrase = ''

    def listen(self) -> None:
        self._invoker.set_on_listen(self._recognize)
        self._invoker.do_listen()

    def say_and_listen(self, *actions) -> None:
        self.push(*actions)
        self._invoker.set_on_speak(self._phrase)
        self._invoker.do_speak()
        # sleep(0.00001)
        self._invoker.set_on_listen(self._recognize)
        self._invoker.do_listen()
        self.last = self._phrase
        self._phrase = ''
