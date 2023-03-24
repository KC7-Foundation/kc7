import requests
import random
import re

#    def __init__(self, 
                # word_source="app/game_configs/gameplay/seed_text.txt"):

class SentenceGenerator:
    """
    based on https://github.com/hrs/markov-sentence-generator
    """

import random

class SentenceGenerator:

    def __init__(self, word_source="app/game_configs/gameplay/seed_text.txt"):
        self.word_source = word_source
        self.load_text()

    def genSentence(self, length=10):
        sentence = ''
        while len(sentence.split()) < length:
            sentence += random.choice(self.words) + ' '
        return sentence.strip().lower().capitalize()


    def load_text(self):
        """
        Load a list of words from a given text url
        """
        if "http" in self.word_source:
            response = requests.get(self.word_source).text
        else:
            with open(self.word_source) as f:
                response = f.read()

        # remove unwanted characters
        table = str.maketrans(dict.fromkeys('#<>-'))
        response = response.translate(table)

        self.words = [self.fix_caps(w) for w in re.findall(r"[\w]+|[.,!?;]", response) if len(w) > 1]


    def fix_caps(self, word):
        """
        Standardize capitalization on words
         We want to be able to compare words independent of their capitalization.
        """
        # Ex: "FOO" -> "foo"
        if word.isupper() and word != "I":
            word = word.lower()
            # Ex: "LaTeX" => "Latex"
        elif word [0].isupper():
            word = word.lower().capitalize()
            # Ex: "wOOt" -> "woot"
        else:
            word = word.lower()
        return word