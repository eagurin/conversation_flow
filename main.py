import models
from command import Invoker
from patterns import (city_ptrn, context_words, entity_ptrn, intent_ptrn,
                      name_ptrn, product_ptrn)
from post import Post
from prompts import prompts_dict
from recognize import Recognize
from stack import PromptStack
from state import Context, State
from utils import clear_html, send_sms


class Menu:

    def menu(self) -> None:
        self.nav()
        self.default()
        self.question()

    def nav(self):
        if self.recognize.entity('delivery') or self.recognize.intent('delivery'):
            self.context.transition_to(Shipping())
            return

        if self.recognize.intent('payments') or self.recognize.entity('payments'):
            self.context.transition_to(Payments())
            return

        if self.recognize.intent('order') or self.recognize.entity('order'):
            self.context.transition_to(Order())
            return

    def default(self):
        if self.entity('repeat'):
            self.phrase.say_and_listen(self.phrase.last)
            self.context.request()

        if self.entity('robot'):
            self.phrase.say_and_listen('robot', 'tail')
            self.context.request()

        if self.entity('busy', 'callback', 'caller'):
            self.context.result('Перезвонить позже')
            self.phrase.push('good', 'hangup_recall')
            self.context.transition_to(Hangup())

        if self.entity('wrong', 'different') and self.entity('phone', 'caller'):
            self.context.result('Ошиблись номером')
            self.phrase.say('hangup_dont_disturb')
            self.context.transition_to(Hangup())

        if self.entity('wait'):
            self.phrase.say_and_listen('good', 'wait')
            while not self.entity('oleg'):
                self.phrase.listen()
            self.phrase.say('comeback')
            self.context.request()

        if self.entity('good_buy'):
            self.context.transition_to(Hangup())

    def question(self):
        if self.entity('question'):
            if self.entity('difference') and self.product('f-hair') and self.product('f-hair man'):
                self.phrase.push('Ф хаир больше направлен на улучшение трофики!')
                self.phrase.push('В его составе есть железо, цинк, магний, которого часто не хватает у женщин при анемии.')
                self.phrase.push('У мужчин такое тоже бывает.')
                self.phrase.push('Ф хаир мэн также улучшает трофику!, но в его составе аналоги миноксиди0ла.')
                self.phrase.push('Они изменяют чувствительность гормонов андрогены на фолли0кул.')
                self.phrase.push('Поэтому, прежде надо выяснить причину выпадения воло0с.')
                self.phrase.push('Бывает, что женщинам подойдёт Ф хаир мэн, а мужчинам просто Ф хаир.')
                self.phrase.say_and_listen('after_success')
                self.context.request()


class Hello(State, Menu):
    entry = None

    def handle(self) -> None:
        if not self.entry:
            self.entry = True
            self.phrase.say_and_listen('hello', self.user.firstname, 'tail')
            self.context.request()


class Shipping(State, Menu):
    method = None

    def handle(self) -> None:
        self.question()
        self.set_on_address()
        self.set_on_city()
        self.set_on_method()
        self.check_city()
        self.check_method()
        self.post.do_clear_address()
        self.check_address()
        self.post.get_delivery_cost()
        self.get_result()

    def set_on_address(self):
        if self.recognize.utterance:
            self.post.set_on_address(self.recognize.utterance)

    def set_on_city(self):
        if self.recognize.city:
            self.post.set_on_city(self.recognize.city)

    def set_on_method(self):
        if self.entity('post'):
            self.post.set_on_method('PARCEL_CLASS_1')
        if self.entity('courier'):
            self.post.set_on_method('EMS')

    def check_city(self):
        if not self.post.city:
            self.phrase.say_and_listen('В какой город будем отправлять?')
            self.context.request()

    def check_address(self):
        if not self.post.index:
            self.phrase.say_and_listen('Назовите ваш адрес?')
            self.post.recognize_address = self.recognize.utterance + ' '
            self.context.request()

    def check_method(self):
        if not self.post.method:
            self.phrase.say_and_listen('Каким способом? Курьером или до пункта самовывоза?')
            self.context.request()

    def get_result(self):
        text = ''
        if self.post.method == 'PARCEL_CLASS_1':
            text = 'до пункта самовывоза '
        if self.post.method == 'EMS':
            text = 'курьером '
        self.phrase.push(f'Доставка {text} в город {self.post.city} будет стоить {self.post.cost} рублей!')
        if self.post.delivery_time == 1:
            day = 'день'
        elif int(str(self.post.delivery_time)[-1]) in [2, 3, 4]:
            day = 'дня'
        elif int(str(self.post.delivery_time)[-1]) in [5, 6, 7, 8, 9, 0]:
            day = 'дней'
        self.phrase.say_and_listen(f'Срок доставки {self.post.delivery_time} {day}')
        self.post.city = None
        self.post.cost = None
        self.post.delivery_time = None
        self.context.request()

    def question(self):
        if self.entity('question') and self.entity('method'):
            if self.entity('post'):
                self.post.method = 'PARCEL_CLASS_1'
                self.phrase.say_and_listen('Мы отправляем заказы до почтовоых отделений Почты России, или пунктов самовывоза СДЭКа и Bo0xberry.')
                self.context.request()
            if self.entity('courier'):
                self.post.method = 'EMS'
                self.phrase.say_and_listen('Мы отправляем заказы курьерами ЕЭМ0С, СДЭКом и Bo0xberry.')
                self.context.request()
            self.phrase.say_and_listen('Мы отправляем заказы Почтой России, СДЭКом и Bo0xberry.')
            self.context.request()


class Payments(State, Menu):
    def handle(self) -> None:
        self.phrase.push('payments_basic')


class Order(State, Menu):
    name = None
    order = None
    order_id = None
    attempt_query = 0

    def handle(self) -> None:
        self.set_user_name()
        self.set_recognized_name()
        self.set_recognized_order_id()
        self.check_name()
        self.check_order_id()
        self.get_order()

    def get_order(self):
        try:
            self.order = models.session.query(models.Order).filter_by(order_id=self.order_id).first()
        except:
            self.order = models.Order()
            self.attempt_query += 1
            if self.attempt_query < 3:
                print('Ошибка запроса', self.attempt_query)
                models.session.rollback()
                self.context.request()
            self.attempt_query = 0

        if not self.order:
            self.phrase.push(f'Не получается найти заказ {self.order_id}')
            self.phrase.say_and_listen('Назовите данные заказа еще раз.')
            self.order_id = None
            self.context.request()

        if self.order.firstname != (self.name or self.user.firstname):
            self.phrase.push(f'В заказе {self.order.order_id} указанно другое имя.')
            self.phrase.say_and_listen(self.user.firstname, 'Назовите данные заказа еще раз!')
            self.name = None
            self.context.request()

        if self.order:
            self.phrase.push(f'Заказ номер {self.order.order_id}.')
            self.phrase.push(f'Статус заказа: {self.order.order_status}.')
            if self.order.track_no:
                self.phrase.push('На ваш номер сейчас придет сообщение с трэк-номером для отслеживания.') 
                send_sms(f'Трек-номер для отслеживания {self.order.track_no}.') 
            self.phrase.push(f'Способ доставки: {clear_html(self.order.shipping_method)}.')
            self.order_id = None
            self.phrase.say_and_listen('after_success')
            self.context.request()

    def set_user_name(self):
        if self.user.firstname:
            self.name = self.user.firstname

    def set_recognized_name(self):
        if self.recognize.name:
            self.name = self.recognize.name

    def set_recognized_order_id(self):
        if self.recognize.digit:
            self.order_id = self.recognize.digit[0]

    def check_name(self):
        if not self.name:
            self.phrase.say_and_listen('what_your_name')
            self.context.request()

    def check_order_id(self):
        if not self.order_id:
            self.phrase.say_and_listen('what_your_order')
            self.context.request()


class Hangup(State, Menu):
    def handle(self) -> None:
        self.say('good_buy')
        self.hangup()


def main(phone):
    try:
        user = models.session.query(models.Customer).filter(models.Customer.telephone==phone).first()
    except:
        print('Ошибка запроса')
    if not user:
        user = models.Customer()
    post = Post()
    invoker = Invoker()
    recognize = Recognize(entity_ptrn, intent_ptrn, name_ptrn, city_ptrn, product_ptrn, context_words)
    phrase = PromptStack(invoker, recognize, prompts_dict)
    context = Context(Hello(), Menu(), user, invoker, phrase, recognize, post)
    context.request()


if __name__ == '__main__':
    phone = '+79103944220'
    main(phone)