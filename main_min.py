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

    
    def handle(self) -> None:
        self.nav()
        self.default()
        self.question()

    def nav(self):
        if entity('delivery') or intent('delivery'):
            context.transition_to(Shipping())
            return

        if intent('payments') or entity('payments'):
            context.transition_to(Payments())
            return

        if intent('order') or entity('order'):
            context.transition_to(Order())
            return

    def default(self):
        if entity('repeat'):
            phrase.say_and_listen(phrase.last)
            context.request()

        if entity('robot'):
            phrase.say_and_listen('robot', 'tail')
            context.request()

        if entity('busy', 'callback', 'caller'):
            context.result('Перезвонить позже')
            phrase.push('good', 'hangup_recall')
            context.transition_to(Hangup())

        if entity('wrong', 'different') and entity('phone', 'caller'):
            context.result('Ошиблись номером')
            phrase.say('hangup_dont_disturb')
            context.transition_to(Hangup())

        if entity('wait'):
            phrase.say_and_listen('good', 'wait')
            while not entity('oleg'):
                phrase.listen()
            phrase.say('comeback')
            context.request()

        if entity('good_buy'):
            context.transition_to(Hangup())

    def question(self):
        if entity('question'):
            if entity('difference') and product('f-hair') and product('f-hair man'):
                phrase.push('Ф хаир больше направлен на улучшение трофики!')
                phrase.push('В его составе есть железо, цинк, магний, которого часто не хватает у женщин при анемии.')
                phrase.push('У мужчин такое тоже бывает.')
                phrase.push('Ф хаир мэн также улучшает трофику!, но в его составе аналоги миноксиди0ла.')
                phrase.push('Они изменяют чувствительность гормонов андрогены на фолли0кул.')
                phrase.push('Поэтому, прежде надо выяснить причину выпадения воло0с.')
                phrase.push('Бывает, что женщинам подойдёт Ф хаир мэн, а мужчинам просто Ф хаир.')
                phrase.say_and_listen('after_success')
                context.request()


class Hello(State, Menu):
    entry = None

    def handle(self) -> None:
        if not self.entry:
            self.entry = True
            phrase.say_and_listen('hello', user.firstname, 'tail')
            context.request()


class Shipping(State, Menu):
    method = None

    def handle(self) -> None:
        self.question()
        self.set_on_address()
        self.set_on_city()
        self.set_on_method()
        self.check_city()
        self.check_method()
        post.do_clear_address()
        self.check_address()
        post.get_delivery_cost()
        self.get_result()

    def set_on_address(self):
        if recognize.utterance:
            post.set_on_address(recognize.utterance)

    def set_on_city(self):
        if recognize.city:
            post.set_on_city(recognize.city)

    def set_on_method(self):
        if entity('post'):
            self.method = 'PARCEL_CLASS_1'
        if entity('courier'):
            self.method = 'EMS'
        post.set_on_method(self.method)

    def check_city(self):
        if not post.city:
            phrase.say_and_listen('В какой город будем отправлять?')
            context.request()

    def check_address(self):
        if not post.index:
            phrase.say_and_listen('Назовите ваш адрес?')
            post.recognize_address = recognize.utterance + ' '
            context.request()

    def check_method(self):
        if not post.method:
            phrase.say_and_listen('Каким способом? Курьером или до пункта самовывоза?')
            context.request()

    def get_result(self):
        text = ''
        if post.method == 'PARCEL_CLASS_1':
            text = 'до пункта самовывоза '
        if post.method == 'EMS':
            text = 'курьером '
        phrase.push(f'Доставка {text} в город {post.city} будет стоить {post.cost} рублей!')
        if post.delivery_time == 1:
            day = 'день'
        elif int(str(post.delivery_time)[-1]) in [2, 3, 4]:
            day = 'дня'
        elif int(str(post.delivery_time)[-1]) in [5, 6, 7, 8, 9, 0]:
            day = 'дней'
        phrase.say_and_listen(f'Срок доставки {post.delivery_time} {day}')
        context.request()

    def question(self):
        if entity('question') and entity('method'):
            if entity('post'):
                self.method = 'PARCEL_CLASS_1'
                phrase.say_and_listen('Мы отправляем заказы до почтовоых отделений Почты России, или пунктов самовывоза СДЭКа и Bo0xberry.')
                context.request()
            if entity('courier'):
                self.method = 'EMS'
                phrase.say_and_listen('Мы отправляем заказы курьерами ЕЭМ0С, СДЭКом и Bo0xberry.')
                context.request()
            phrase.say_and_listen('Мы отправляем заказы Почтой России, СДЭКом и Bo0xberry.')
            context.request()


class Payments(State, Menu):
    def handle(self) -> None:
        phrase.push('payments_basic')


class Order(State, Menu):
    name = None
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
            order = models.session.query(models.Order).filter_by(order_id=self.order_id).first()
        except:
            order = models.Order()
            self.attempt_query += 1
            if self.attempt_query < 3:
                print('Ошибка запроса', self.attempt_query)
                models.session.rollback()
                context.request()
            self.attempt_query = 0

        if not order:
            phrase.push(f'Не получается найти заказ {self.order_id}')
            phrase.say_and_listen('Назовите данные заказа еще раз.')
            self.order_id = None
            context.request()

        if order.firstname != (self.name or user.firstname):
            phrase.push(f'В заказе {order.order_id} указанно другое имя.')
            phrase.say_and_listen(user.firstname, 'Назовите данные заказа еще раз!')
            self.name = None
            context.request()

        if order:
            phrase.push(f'Заказ номер {order.order_id}.')
            phrase.push(f'Статус заказа: {order.order_status}.')
            if order.track_no:
                phrase.push('На ваш номер сейчас придет сообщение с трэк-номером для отслеживания.') 
                send_sms(f'Трек-номер для отслеживания {order.track_no}.') 
            phrase.push(f'Способ доставки: {clear_html(order.shipping_method)}.')
            self.order_id = None
            phrase.say_and_listen('after_success')
            context.request()

    def set_user_name(self):
        if user.firstname:
            self.name = user.firstname

    def set_recognized_name(self):
        if recognize.name:
            self.name = recognize.name

    def set_recognized_order_id(self):
        if recognize.digit:
            self.order_id = recognize.digit[0]

    def check_name(self):
        if not self.name:
            phrase.say_and_listen('what_your_name')
            context.request()

    def check_order_id(self):
        if not self.order_id:
            phrase.say_and_listen('what_your_order')
            context.request()


class Hangup(State, Menu):
    def handle(self) -> None:
        self.say('good_buy')
        self.hangup()


if __name__ == '__main__':
    phone = '+79103944220222'
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
    context = Context(Hello(), Menu(), Shipping(), Payments(), Order(), Hangup(), user, invoker, phrase, recognize)
    intent = recognize.intent
    entity = recognize.entity
    product = recognize.product
    context.request()
