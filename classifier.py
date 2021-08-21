import pandas as pd
import numpy as np
from tqdm import tqdm
from preprocess import Preprocess
import fasttext
from unidecode import unidecode
import os 
from collections import Counter
import googletrans 
from sklearn.model_selection import train_test_split


from sklearn.metrics import classification_report, confusion_matrix

def score(y_true, y_pred):
    print(f"Classification Report \n {classification_report(y_true, y_pred)}")
    
def load_posts():
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


ft_data = {'train':[], 'test':[]}

for d, l in zip(X_train, y_train):
    if(l==0):
        ft_data['train'].append("__label__negative " + d+ " \n")
    elif(l==2):
        ft_data['train'].append("__label__positive " + d+ " \n")
    else:
        print("sentiment not recognized")
for d, l in zip(X_test, y_test):
    if(l==0):
        ft_data['test'].append("__label__negative " + d+ " \n")
    elif(l==2):
        ft_data['test'].append("__label__positive " + d+ " \n")
    else:
        print("sentiment not recognized")


if(os.path.exists(f"ft_train_preprocessed.txt") and os.path.exists(f"ft_test_preprocessed.txt")):
    print("removing old training/test txt files")
    os.remove(f"ft_train_preprocessed.txt")
    os.remove(f"ft_test_preprocessed.txt")
open(f"ft_train_preprocessed.txt","w",  encoding='utf-8').writelines(ft_data['train']) 
open(f"ft_test_preprocessed.txt","w", encoding='utf-8').writelines(ft_data['test']) 

import fasttext

hyper_params={'lr': 0.1, 'epoch': 10,'wordNgrams': 2, 'ws': 2, 'minn': 3, 'maxn': 6, 'verbose': 1, 'dim': 300}
     
print(hyper_params)
model = fasttext.train_supervised(input=f'ft_train_preprocessed.txt', **hyper_params)

print(f"TRAIN ACCURACY: {model.test(f'ft_train_preprocessed.txt')}")
print(f"TEST ACCURACY: {model.test(f'ft_test_preprocessed.txt')}")

y_preds = []
test_data = open(f'ft_test_preprocessed.txt',"r",  encoding='utf-8')
for text in test_data:
  y_pred = model.predict(text.strip())
  y_preds.append(y_pred)

y_preds = [{'__label__negative':0, '__label__neutral':1, '__label__positive':2} [y[0][0]] for y in y_preds]

score(y_true=y_test, y_pred=y_preds)
 