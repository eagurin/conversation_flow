from abc import ABC

import models
from command import Invoker
from patterns import (city_ptrn, context_words, entity_ptrn, intent_ptrn,
                      name_ptrn, product_ptrn)
from prompts import prompts_dict
from recognize import Recognize
from stack import PromptStack
from state import Context, State
from utils import clear_html, send_sms


class Main(ABC):
    def menu(self) -> None:
        self.question()
        self.navigation()
        self.default()

    def question(self):
        if (self.entity('difference') or self.entity('question')) and (self.product('f-hair') and self.product('f-hair man')):
            self.push('Ф хаир больше направлен на улучшение трофики!')
            self.push('В его составе есть железо, цинк, магний, которого часто не хватает у женщин при анемии.')
            self.push('У мужчин такое тоже бывает.')
            self.push('Ф хаир мэн также улучшает трофику!, но в его составе аналоги миноксиди0ла.')
            self.push('Они изменяют чувствительность гормонов андрогены на фолли0кул.')
            self.push('Поэтому, прежде надо выяснить причину выпадения.')
            self.push('Бывает, что женщинам подойдёт Ф хаир мэн, а мужчинам просто Ф хаир.')
            self.say_and_listen('after_success')
            self.menu()
            self.request()

    def navigation(self):
        if self.entity('delivery'):
            self.transition_to(Delivery())
            self.request()

        if self.intent('payments') or self.entity('payments'):
            self.transition_to(Payments())
            self.request()

        if self.intent('order') or self.entity('order'):
            self.transition_to(Order())
            self.request()

    def default(self):
        if self.entity('wait'):
            self.say('good', 'wait')
            self.r.entities = []
            while not self.entity('oleg'):
                self.listen()
            self.say_and_listen('comeback', 'tail')
            self.menu()
            self.request()

        if self.entity('busy', 'callback', 'caller'):
            self.result('Перезвонить позже')
            self.push('good', 'hangup_recall')
            self.hangup()
            self.menu()
            self.request()

        if self.entity('wrong', 'different') and self.entity('phone', 'caller'):
            self.result('Ошиблись номером')
            self.say('hangup_dont_disturb', 'good_buy')
            self.hangup()
            self.menu()
            self.request()

        if self.entity('repeat'):
            self.say_and_listen(self.phrase._last_phrase)
            self.menu()
            self.request()

        if self.entity('robot'):
            self.say_and_listen('robot', 'tail')
            self.menu()
            self.request()

        if self.entity('good_buy'):
            self.hangup()

    def hangup(self):
        self.say('good_buy')
        self.context._hangup = True
        self.request()


class Hello(State, Main):
    enter = None

    def handle(self) -> None:
        if not self.enter:
            self.name = self.user.firstname or ''
            self.say_and_listen('hello', self.name, 'tail')
            self.enter = True
            self.menu()
            self.request()

        self.say_and_listen('tail')
        self.menu()
        self.request()


class Delivery(State, Main):
    def handle(self) -> None:
        if self.entity('when') and self.entity('cost'):
            self.say_and_listen('delivery_cost_time', 'tail')
            self.menu()
            self.request()

        if self.entity('when'):
            self.say_and_listen('delivery_time', 'tail')
            self.menu()
            self.request()

        if self.entity('cost'):
            self.say_and_listen('delivery_cost', 'tail')
            self.menu()
            self.request()

        self.say_and_listen('delivery_basic', 'tail')
        self.menu()
        self.request()


class Payments(State, Main):
    def handle(self) -> None:
        self.say_and_listen('payments_basic', 'tail')
        self.menu()
        self.request()


class Order(State, Main):
    count = 0
    user = None
    name = None
    order = None
    order_id = None
    order_status = None
    attempt_query = 0

    def handle(self) -> None:
        self.counter()
        self.check_name()
        self.check_order_id()
        self.get_order()

    def counter(self):
        self.count += 1
        if self.count > 7:
            self.push('Хватит морочить мне голову!')
            self.hangup()
            self.request()

    def check_required_fields(self):
        self.check_name()
        self.check_order_id()

    def check_name(self):
        self.save_form_field()
        if not self.name:
            self.say_and_listen('what_your_name')
            self.save_form_field()
            self.menu()

    def check_order_id(self):
        self.save_form_field()
        if not self.order_id:
            self.say_and_listen('what_your_order')
            self.save_form_field()
            self.menu()

    def get_order(self):
        order = models.Order()
        try:
            order = models.session.query(models.Order).filter_by(order_id=self.order_id).first()
        except:
            self.attempt_query += 1
            if self.attempt_query < 3:
                models.session.rollback()
                self.menu()
                self.request()
            self.attempt_query = 0
            print('Ошибка запроса', self.attempt_query)

        if not order:
            self.push(f'Не получается найти заказ: {self.order_id}')
            self.say_and_listen('Назовите данные заказа еще раз.')
            self.order_id = None
            self.save_form_field()
            self.menu()
            self.request()

        if order.firstname != self.name:
            self.push(f'В заказе {order.order_id} указанно другое имя.')
            self.say_and_listen(self.name, 'Назовите данные заказа еще раз!')
            self.order_id = None
            self.save_form_field()
            self.menu()
            self.request()

        if order:
            self.push(f'Заказ номер {order.order_id}.')
            self.push(f'Статус заказа: {order.order_status}.')
            if order.track_no:
                self.push('На ваш номер сейчас придет сообщение с трэк-номером для отслеживания.') 
                send_sms(f'Трек-номер для отслеживания: {order.track_no}.') 
            self.push(f'Способ доставки: {clear_html(order.shipping_method)}.')
            self.say_and_listen('after_success')
            self.order_id = None
            self.menu()
            self.request()

    def save_form_field(self) -> None:
        self.set_name()
        self.set_order_id()
    
    def set_name(self):
        if self.user.firstname:
            self.name = self.user.firstname
        if self.r.name:
            self.name = self.r.name

    def set_order_id(self):
        if self.r.digit:
            self.order_id = self.r.digit[0]


def main():
    phone = '9103944220'
    try:
        user = models.session.query(models.Customer).filter(models.Customer.telephone==phone).one()
    except:
        user = models.Customer()
        print('Ошибка запроса')
    invoker = Invoker()
    recognize = Recognize(entity_ptrn, intent_ptrn, name_ptrn, city_ptrn, product_ptrn, context_words)
    phrase = PromptStack(invoker, recognize, prompts_dict)
    context = Context(Hello(), user, invoker, phrase, recognize)
    context.request()


if __name__ == '__main__':
    main()
