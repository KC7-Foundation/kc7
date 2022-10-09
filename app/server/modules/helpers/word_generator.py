import requests
import random


class WordGenerator:
    
    def __init__(self, word_site="http://www.mieliestronk.com/corncob_lowercase.txt"):
        
        self.word_source = word_site
        self.load_words()
    
    def load_words(self):
            
        response = requests.get(self.word_source)
        self.words = response.content.decode('utf-8').splitlines()
            
    def get_word(self) -> str:
        return random.choice(self.words)
        
    def get_words(self, count_words=2) -> list:
        return random.choices(self.words, k=count_words)