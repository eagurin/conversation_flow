import sys

import models
from command import Invoker
from patterns import city, context_words, entity, intent, name, product
from post import Post
from prompts import prompts_dict
from recognize import Recognize
from stack import PromptStack
from utils import add_days, clear_html, send_sms


class Context:
    _call_counter = 0
    _state_counter = 0

    def __init__(self, state, user, invoker, phrase, recognize, post):
        self._user = user
        self._invoker = invoker
        self._recognize = recognize
        self._phrase = phrase
        self._post = post
        self.last_state = state
        self.transition_to(state)

    def transition_to(self, state):
        print("\nState:", type(state).__name__)
        self._state = state
        self._state.user = self._user
        self._state.post = self._post or Post()
        self._state.recognize = self._recognize
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
        self._state.hangup = self.hangup
        self._state.transition_to = self.transition_to
        self._state.context = self

    def request(self):
        self.counter()
        self._state.question()
        self._state.navigation()
        self._state.basic()
        self._state.handle()
        self._phrase.say_and_listen('tail')
        self.request()

    def hangup(self):
        print('\nЗвонок завершен.\n')
        sys.exit()

    def state_name(self):
        return type(self._state).__name__

    def result(self, text):
        self._result = text
        print("\nResult:", text)

    def counter(self):
        self._call_counter += 1
        self._state_counter += 1
        if self._state != self.last_state:
            self._state_counter = 1
        if self._call_counter > 50:
            self._phrase.say('Что-то мы с вами заговорились!', 'А время- деньги!!')
            self.hangup()
        if self._state_counter > 10:
            self._phrase.say('Хватит морочить мне голову!')
            self.hangup()


class Main:
    
    def handle(self):
        self.navigation()
        self.basic()
        self.question()

    def navigation(self):
        if self.entity('delivery') or self.intent('delivery'):
            self.transition_to(Shipping())
            return

        if self.intent('payments') or self.entity('payments'):
            self.transition_to(Payments())
            return

        if self.intent('order') or self.entity('order'):
            self.transition_to(Order())
            return

    def basic(self):
        if self.entity('repeat'):
            self.say_and_listen(self.phrase.last)
            self.request()

        if self.entity('robot'):
            self.say_and_listen('robot', 'tail')
            self.request()

        if self.entity('busy', 'callback', 'caller'):
            self.result('Перезвонить позже')
            self.push('good', 'hangup_recall')
            self.transition_to(Hangup())

        if self.entity('wrong', 'different') and self.entity('phone', 'caller'):
            self.result('Ошиблись номером')
            self.say('hangup_dont_disturb')
            self.transition_to(Hangup())

        if self.entity('wait'):
            self.say_and_listen('good', 'wait')
            while not self.entity('oleg'):
                self.listen()
            self.say('comeback')
            self.request()

        if self.entity('good_buy'):
            self.transition_to(Hangup())

    def question(self):
        if self.entity('question', 'when', 'cost', 'info', 'where', 'difference'):
            if self.product('f-hair') and self.product('f-hair man'):
                self.push('Ф хаир больше направлен на улучшение трофики!')
                self.push('В его составе есть железо, цинк, магний, которого часто не хватает у женщин при анемии.')
                self.push('У мужчин такое тоже бывает.')
                self.push('Ф хаир мэн также улучшает трофику!, но в его составе аналоги миноксиди0ла.')
                self.push('Они изменяют чувствительность гормонов андрогены на фолли0кул.')
                self.push('Поэтому, прежде надо выяснить причину выпадения воло0с.')
                self.push('Бывает, что женщинам подойдёт Ф хаир мэн, а мужчинам просто Ф хаир.')
                self.say_and_listen('after_success')
                self.request()

        if self.entity('delivery') and self.context.state_name() != 'Shipping':
            if self.entity('post'):
                self.say_and_listen(
                    'Мы отправляем заказы до отделений Почты России, или пунктов самовывоза СДЭКа и Bo0xberry.',
                    'Вы хотите расчитать стоимость и время доставки?'
                )
                if self.entity('yes'):
                    self.post.set_on_method('PARCEL_CLASS_1')
                    self.push('good')
                    self.transition_to(Shipping())
                    self.request()

            if self.entity('courier'):
                self.say_and_listen(
                    'Мы отправляем заказы курьерами: ЕЭМ0С, СДЭКом и Bo0xberry.',
                    'Вы хотите расчитать стоимость и время доставки?'
                )
                if self.entity('yes'):
                    self.post.set_on_method('EMS')
                    self.push('good')
                    self.transition_to(Shipping())
                    self.request()

            if self.entity('method'):
                self.say_and_listen(
                    'Мы отправляем заказы Почтой России, СДЭКом и Bo0xberry.',
                    'Вы хотите расчитать стоимость и время доставки?'
                )
                if self.entity('yes'):
                    self.push('good')
                    self.transition_to(Shipping())
                    self.request()


class Hello(Main):
    entry = None

    def handle(self) -> None:
        if not self.entry:
            self.entry = True
            if self.user.firstname:
                self.say_and_listen('hello', self.user.firstname, 'tail')
                self.request()

            self.say_and_listen('hello', 'what_your_name')
            if self.recognize.name:
                self.user.firstname = self.recognize.name
                self.push('glad_to_meet_you', self.user.firstname)
            self.request()


class Shipping(Main):

    def handle(self) -> None:
        self.question()
        self.set_on_address()
        self.set_on_city()
        self.set_on_method()
        self.check_city()
        self.check_method()
        self.do_clear_address()
        self.check_address()
        self.get_delivery_cost()
        self.get_result()
        self.result_clear()
        self.transition_to(Main())
        self.request()

    def set_on_address(self):
        if self.recognize.utterance:
            self.post.set_on_address(self.recognize.utterance)

    def set_on_city(self):
        if self.recognize.city:
            self.post.set_on_city(self.recognize.city)

    def set_on_method(self):
        if self.entity('post'):
            self.method_text = 'до пункта самовывоза '
            self.post.set_on_method('PARCEL_CLASS_1')
        if self.entity('courier'):
            self.method_text = 'курьером '
            self.post.set_on_method('EMS')

    def check_city(self):
        if not self.post.city:
            self.say_and_listen('В какой город будем отправлять?')
            self.request()

    def check_method(self):
        if not self.post.method:
            self.say_and_listen('Каким способом? Курьером или до пункта самовывоза?')
            self.request()

    def do_clear_address(self):
        self.post.do_clear_address()

    def check_address(self):
        if not self.post.index:
            self.say_and_listen('Назовите ваш адрес?')
            self.request()

    def get_delivery_cost(self):
        self.post.get_delivery_cost()

    def get_result(self):
        self.push(f'Доставка {self.post.method_text} в город {self.post.city} будет стоить {self.post.cost} рублей!')
        self.push(f'Срок доставки {add_days(self.post.delivery_time)}')
        self.say_and_listen('after_success')
        if self.entity('post') or self.entity('courier'):
            self.request()

    def result_clear(self):
        self.context._post = None


class Payments(Main):
    def handle(self) -> None:
        self.push('payments_basic')


class Order(Main):
    name = None
    order = None
    order_id = None
    attempt_query = 0

    def handle(self) -> None:
        self.set_user_firstname()
        self.set_recognized_name()
        self.set_recognized_order_id()
        self.check_field_order_id()
        self.check_field_name()
        self.request_order()
        self.check_order()
        self.check_name_in_order()
        self.result_order()

    def set_user_firstname(self):
        if self.user.firstname:
            self.name = self.user.firstname

    def set_recognized_name(self):
        if self.recognize.name:
            self.name = self.recognize.name

    def set_recognized_order_id(self):
        if self.recognize.digit:
            self.order_id = self.recognize.digit[0]

    def check_field_order_id(self):
        if not self.order_id:
            self.say_and_listen('what_your_order')
            self.request()

    def check_field_name(self):
        if not self.name:
            self.say_and_listen('what_your_name_order')
            self.request()

    def request_order(self):
        try:
            self.order = models.session.query(models.Order).filter_by(order_id=self.order_id).first()
        except:
            self.attempt_query += 1
            if self.attempt_query < 3:
                models.session.rollback()
                self.request()
            print('\nОшибка запроса')
            self.order = models.Order()
            self.attempt_query = 0

    def check_order(self):
        if not self.order:
            self.push(f'Не получается найти заказ {self.order_id}')
            self.say_and_listen('Назовите данные заказа еще раз.')
            self.order_id = None
            self.request()
 
    def check_name_in_order(self):
        if self.recognize.name and self.recognize.name != self.order.firstname:
            self.push(f'Имя: {self.name}- не подходит для заказа: {self.order.order_id}.')
            self.say_and_listen(f'{self.user.firstname}, назовите данные заказа еще раз!')
            self.request()
        elif self.recognize.name == self.order.firstname:
            return
        if self.user.firstname != self.order.firstname:
            self.push(f'В заказе: {self.order.order_id}, указанно не ваше имя.')
            self.say_and_listen(f'{self.user.firstname}, назовите данные заказа еще раз!')
            self.order_id = None
            self.request()

    def result_order(self):
        self.push(f'Заказ номер {self.order.order_id}.')
        if self.order.order_status:
            self.push(f'Статус заказа: {self.order.order_status}.')
        if self.order.track_no:
            self.push('На ваш номер сейчас придет сообщение с трэк-номером для отслеживания.') 
            send_sms(f'Трек-номер для отслеживания {self.order.track_no}.') 
        self.push(f'Способ доставки: {clear_html(self.order.shipping_method)}.')
        self.order_id = None
        self.say_and_listen(self.user.firstname, 'after_success')
        self.request()


class Hangup(Main):
    def handle(self) -> None:
        self.say('good_buy')
        self.hangup()


def main(phone):
    user = None
    try:
        user = models.session.query(models.Customer).filter(models.Customer.telephone==phone).first()
    except:
        print('Ошибка запроса')
    if not user:
        user = models.Customer()
    post = Post()
    invoker = Invoker()
    recognize = Recognize(entity, intent, name, city, product, context_words)
    phrase = PromptStack(invoker, recognize, prompts_dict)
    context = Context(Hello(), user, invoker, phrase, recognize, post)
    context.request()


if __name__ == '__main__':
    phone = '+79103944220'
    main(phone)
