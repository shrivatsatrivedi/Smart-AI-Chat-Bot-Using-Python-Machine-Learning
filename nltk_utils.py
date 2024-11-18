import numpy as np
import nltk
from nltk.corpus import wordnet
from nltk.stem.porter import PorterStemmer

nltk.download('punkt')
nltk.download('wordnet')

stemmer = PorterStemmer()

def tokenize(sentence):
    """
    Split sentence into array of words/tokens.
    A token can be a word or punctuation character, or number.
    """
    return nltk.word_tokenize(sentence.lower())  # Convert to lowercase

def stem(word):
    """
    Stemming = find the root form of the word.
    Examples:
    words = ["organize", "organizes", "organizing"]
    words = [stem(w) for w in words]
    -> ["organ", "organ", "organ"]
    """
    return stemmer.stem(word.lower())

def get_synonyms(word):
    """
    Get a list of synonyms for a given word using WordNet.
    """
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(stem(lemma.name()))
    return synonyms

def bag_of_words(tokenized_sentence, words):
    """
    Return bag of words array:
    1 for each known word that exists in the sentence, 0 otherwise.
    Example:
    sentence = ["hello", "how", "are", "you"]
    words = ["hi", "hello", "I", "you", "bye", "thank", "cool"]
    bog   = [  0 ,    1 ,    0 ,   1 ,    0 ,    0 ,      0]
    """
    # Stem each word in the sentence
    sentence_words = [stem(word) for word in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)
    
    for idx, w in enumerate(words):
        w_stem = stem(w)
        synonyms = get_synonyms(w)  # Get synonyms for the word in the vocabulary
        if w_stem in sentence_words or any(syn in sentence_words for syn in synonyms):
            bag[idx] = 1

    return bag