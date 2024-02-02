import spacy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def initialize_nlp():
    nlp = spacy.load("en_core_web_sm")
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    return nlp, sia