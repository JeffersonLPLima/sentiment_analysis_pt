import pandas as pd
import numpy as np
from tqdm import tqdm
from preprocess import Preprocess
import fasttext
from unidecode import unidecode
import os 
from collections import Counter
 
from sklearn.model_selection import train_test_split

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.metrics import classification_report, confusion_matrix

def score(y_true, y_pred):
    print(f"Classification Report \n {classification_report(y_true, y_pred)}")
    
from sklearn.metrics import classification_report, confusion_matrix

def score(y_true, y_pred):
    print(f"Classification Report \n {classification_report(y_true, y_pred)}")
    
def load_posts():
    import googletrans
    df = pd.read_csv('data/sentiment140/training.1600000.processed.noemoticon.csv', header=None, encoding='ISO-8859-1', names= ["target", "ids", "date", "flag", "user", "text"])
    print("sentiment140")
    print(df.head())
    sent_data = [(p, {0:0, 4:2}[t]) for p, t in df[['text', 'target']].to_numpy()]
    pt_sent_data = []
    translator = googletrans.Translator()

    for sd in sent_data:
        pt_post = translator.translate(sd[0], src='en', dest='pt').text
        pt_sent_data.append((pt_post,sd[1]))

    return pt_sent_data


 
sentiment140_data = load_posts()

X, y = [p[0] for p in sentiment140_data],[p[1] for p in sentiment140_data]


X, y =  Preprocess().fit_transform(X, y)
 
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.25, random_state=23)
 

print(f"Proportion of classes on train set: {Counter(y_train)}")
print(f"Proportion of classes on test set: {Counter(y_test)}")

tfidf =  TfidfVectorizer(ngram_range=(1, 2),lowercase=True, token_pattern=r'[^\s]+')

vectors = tfidf.fit_transform(X_train)

model = ComplementNB(class_prior=[0.25, 0.5, 0.25])
model.fit(vectors, y_train)

print(f"score on train: {model.score(vectors, y_train)}")
print(f"score on test:  {model.score( tfidf.transform(X_test), y_test)}")

