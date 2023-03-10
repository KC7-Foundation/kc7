import requests
import random


class WordGenerator:
    
    def __init__(self, word_site="app/server/modules/helpers/corncob_lowercase.txt"):
        
        self.word_source = word_site
        self.load_words()
    
    def load_words(self):
        
        if "http" in self.word_source:
            response = requests.get(self.word_source)
            self.words = response.content.decode('utf-8').splitlines()
        else:
            with open(self.word_source, 'r') as f:
                response = f.read()
            self.words = response.splitlines()
        
            
    def get_word(self) -> str:
        return random.choice(self.words)
        
    def get_words(self, count_words=2) -> list:
        return random.choices(self.words, k=count_words)