import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import numpy as np

stemmer=PorterStemmer()


def tokenize(sentence : str):
    return word_tokenize(sentence)

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence,words):
    sentence_words=[stem(word) for word in tokenized_sentence]
    bag=np.zeros(len(words),dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words: 
            bag[idx] = 1

    return bag


