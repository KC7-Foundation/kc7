import requests
import random
import re

class SentenceGenerator:
    """
    based on https://github.com/hrs/markov-sentence-generator
    """

    def __init__(self, 
                word_site="https://raw.githubusercontent.com/wess/iotr/master/lotr.txt"):
        
        self.word_site = word_site
        self.load_words()
        self.markovLength = 1

        # (tuple of words) -> {dict: word -> number of times the word appears following the tuple}
        # Example entry:
        #    ('eyes', 'turned') => {'to': 2.0, 'from': 1.0}
        # Used briefly while first constructing the normalized self.mapping
        self.tempMapping = {}

        # (tuple of words) -> {dict: word -> *normalized* number of times the word appears following the tuple}
        # Example entry:
        #    ('eyes', 'turned') => {'to': 0.66666666, 'from': 0.33333333}
        self.mapping = {}

        # Contains the set of words that can start sentences
        self.starts = []

        self.buildMapping()


    def load_words(self):
        """
        Load a list of words from a given text url
        """
        response = requests.get(self.word_site).text

        # remove unwanted characters
        table = str.maketrans(dict.fromkeys('#<>-'))
        response = response.translate(table)


        self.wordlist = [self.fix_caps(w) for w in re.findall(r"[\w]+|[.,!?;]", response)]
    

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


    # Building and normalizing the self.mapping.
    def buildMapping(self):
        self.starts.append(self.wordlist [0])
        for i in range(1, len(self.wordlist) - 1):
            if i <= self.markovLength:
                history = self.wordlist[: i + 1]
            else:
                history = self.wordlist[i - self.markovLength + 1 : i + 1]
            follow = self.wordlist[i + 1]
            # if the last elt was a period, add the next word to the start list
            if history[-1] == "." and follow not in ".,!?;":
                self.starts.append(follow)
            self.addItemToTempMapping(history, follow)
        # Normalize the values in self.tempMapping, put them into self.mapping
        for first, followset in self.tempMapping.items():
            total = sum(followset.values())
            # Normalizing here:
            self.mapping[first] = dict([(k, v / total) for k, v in followset.items()])



    def addItemToTempMapping(self, history, word):
        """
        # Self-explanatory -- adds "word" to the "tempMapping" dict under "history".
        # self.tempMapping (and self.mapping) both match each word to a list of possible next
        # words.
        # Given history = ["the", "rain", "in"] and word = "Spain", we add "Spain" to
        # the entries for ["the", "rain", "in"], ["rain", "in"], and ["in"].
        """    
        while len(history) > 0:
            first = SentenceGenerator.toHashKey(history)
            if first in self.tempMapping:
                if word in self.tempMapping[first]:
                    self.tempMapping[first][word] += 1.0
                else:
                    self.tempMapping[first][word] = 1.0
            else:
                self.tempMapping[first] = {}
                self.tempMapping[first][word] = 1.0
            history = history[1:]



    @staticmethod
    def toHashKey(lst):
        """
        # Tuples can be hashed; lists can't.  We need hashable values for dict keys.
        # This looks like a hack (and it is, a little) but in practice it doesn't
        # affect processing time too negatively.
        """
        return tuple(lst)



    def next(self, prevList:list) -> str:
        """
        Returns the next word in the sentence (chosen randomly),
        given the previous ones.
        """
        sum = 0.0
        retval = ""
        index = random.random()
        # Shorten prevList until it's in mapping
        while SentenceGenerator.toHashKey(prevList) not in self.mapping:
            prevList.pop(0)
        # Get a random word from the mapping, given prevList
        for k, v in self.mapping[SentenceGenerator.toHashKey(prevList)].items():
            sum += v
            if sum >= index and retval == "":
                retval = k
        return retval


    def genSentence(self, 
                    markovLength:int=1, 
                    minSentenceLength:int=6, 
                    maxSentenceLength:int=12, 
                    seedWords:list=[]) -> str:
        """
        Generate a markov sentence, 
        given sentence length parameter and seed actor words
        """

        # case: User provides invalid sentence parameters
        if maxSentenceLength < minSentenceLength:
            maxSentenceLength = minSentenceLength
        # sentenceLength must be greated than 2
        if minSentenceLength < 3:
            minSentenceLength = 3
            maxSentenceLength = 3

        # length of sentence is a random length within specified bounds
        sentenceLength = random.randint(minSentenceLength, maxSentenceLength)

        # Start with a random "starting word"
        curr = random.choice(self.starts)
        sentence = curr.capitalize()
        prevList = [curr]
        # Keep adding words until we hit a period
        # while (curr not in "."):
        while len(sentence.split(" ")) < sentenceLength:
            curr = self.next(prevList)
            prevList.append(curr)
            # if the prevList has gotten too long, trim it
            if len(prevList) > markovLength:
                prevList.pop(0)
            if (curr not in ".,!?;"):
                sentence += " " # Add spaces between words (but not punctuation)
            sentence += curr

        # Author comment: this code is bad and I should feed bad D:<
        # this is chaotic but will work for now
        # take a the sentence as str and split on " " into a list
        # inject one or two actor words into the sentence
        # we don't want injected "actor" words to repeat
        sentence = sentence.split(" ")
        # we have a local version of seedwords so we can remove items without having call
        for i in range(random.randint(1,2)):
            insertPosition = random.randint(1, maxSentenceLength-2)
            if any(seedWords):
                # take a words from seenWords and pops it from list
                wordToAdd = seedWords.pop(random.randrange(len(seedWords)))
                sentence.insert(insertPosition, wordToAdd)

        return " ".join(sentence).capitalize()