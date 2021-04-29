import re

from utils import clear, print_


class Recognize():
    """
    Named Entity and Intent Detector
    """
    def __init__(self, entity_ptrn, intent_ptrn, name_ptrn, city_ptrn, product_ptrn, context_words):
        self.entities_ptrn = entity_ptrn
        self.intents_ptrn = intent_ptrn
        self.name_ptrn = name_ptrn
        self.city_ptrn = city_ptrn
        self.product_ptrn = product_ptrn
        self.context_words = context_words
        self.entities = []
        self.intents = []
        self.name = ""
        self.digit = []

    def recognition_utterance(self, responses):
        try:
            for response in responses:
                for result in response.results:
                    for alternative in result.recognition_result.alternatives:
                        print(alternative.transcript)
            self.utterance = alternative.transcript
            print("Phrase start:", result.recognition_result.start_time.ToTimedelta())
            print("Phrase end:  ", result.recognition_result.end_time.ToTimedelta())
        except Exception as e:
            print("Got exception in recognition_utterance", e)
            raise

    def search_entities(self):
        self.entities = []
        for pattern_name in self.entities_ptrn:
            if re.findall(self.entities_ptrn[pattern_name], self.utterance.lower()):
                self.entities.append(pattern_name)
        print_("\nEntities", self.entities)

    def search_intents(self):
        self.intents = []
        for pattern_name in self.intents_ptrn:
            if re.findall(self.intents_ptrn[pattern_name], self.utterance.lower()):
                self.intents.append(pattern_name)
        print_("\nIntents", self.intents)

    def search_products(self):
        self.products = []
        for pattern_name in self.product_ptrn:
            if re.findall(self.product_ptrn[pattern_name], self.utterance.lower()):
                self.products.append(pattern_name)
        print_("\nProducts", self.products)

    def search_name(self):
        self.name = ""
        for word in self.utterance.lower().split():
            if re.findall(self.name_ptrn, word):
                self.name = (clear(word)).title()
                print_("\nName", self.name)
                return

    def search_city(self):
        utterance = clear(self.utterance).split()
        self.city = ""
        tmp = []
        while len(utterance) >= 2:
            word1 = utterance.pop(0).title()
            word2 = utterance[0].title()
            tmp.append(word1)
            word = word1 + ' ' + word2
            self.search_city_(word)
        tmp.append(utterance.pop(0).title())
        for word in tmp:
            self.search_city_(word)

    def search_city_(self, word):
        if re.findall(self.city_ptrn, word):
            self.city = word
            print_("\nCity", self.city)
            return

    def search_digit(self):
        self.digit = []
        self.digit = re.findall('\d+', self.utterance)
        print_("\nDigit", " ".join(self.digit))

    def entity(self, *entity):
        for item in entity:
            if item in self.entities:
                return True

    def intent(self, *intent):
        for item in intent:
            if item in self.intents:
                return True

    def product(self, *product):
        for item in product:
            if item in self.products:
                return True
