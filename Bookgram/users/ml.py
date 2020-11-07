import os
import sys
import numpy as np
import pandas as pd
import sklearn
# import matplotlib.pyplot as plt
# %matplotlib inline
# import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
# import keras
# from keras.models import Sequential, Model
# from keras.layers import Dense, Input
# from keras.utils import plot_model
# from keras.layers import Flatten, Embedding
# from keras.layers.convolutional import Conv2D
# from keras.layers.pooling import MaxPooling2D
# from keras.layers.recurrent import LSTM
# from keras.layers import Concatenate, Dot
# from keras.optimizers import Adam

import datetime
from scipy import stats
from scipy.stats import pearsonr
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import linear_kernel
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import RegexpTokenizer
import re
import string
import random
from PIL import Image
# import requests
from io import BytesIO
from collections import Counter


df_ratings = pd.read_csv('../../dataset/ratings.csv')
df_books = pd.read_csv('../../dataset/books.csv')

print(df_ratings.head(10))
print(df_books.head(10))

books_df = df_books[['book_id','original_title','authors','original_publication_year']]
books_df = books_df.sort_values('book_id')
print(books_df)

print(df_ratings.shape," ",books_df.shape)
print(df_books.columns)

book_tags = pd.read_csv('../../dataset/book_tags.csv')
print(book_tags.head())

tags = pd.read_csv('../../dataset/tags.csv')
print(tags)

merge_tags = pd.merge(book_tags, tags, left_on='tag_id',
                      right_on='tag_id', how='inner')
print(merge_tags)

tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),
                     min_df=0, stop_words='english')

tfidf_matrix_auth = tf.fit_transform(df_books['authors'])
cosine_sim_auth = linear_kernel(tfidf_matrix_auth, tfidf_matrix_auth)

print(cosine_sim_auth)

titles = df_books['title']
indices = pd.Series(df_books.index, index=df_books['title'])

def authors_recom(title, n):    
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim_auth[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    book_indices = [i[0] for i in sim_scores]
    
    return list(titles.iloc[book_indices])

# list1=['Romeo and Juliet','The Hobbit']
def list_to_underscore_list(list_space):
    list_underscore=[]
    for i in list_space:
        j= '_'.join(i.split(' '))
        list_underscore.append(j)

    return list_underscore
    
def recom_list_auth(list1):
    for name in list1:
        recom=authors_recom(name, 10)
        list_out=list_to_underscore_list(recom)
        print (list_out)
    
recom_list_auth(list1)

book_tags = pd.merge(df_books, merge_tags, left_on='book_id',
                     right_on='goodreads_book_id', how='inner')

tfidf_matrix_tag = tf.fit_transform(book_tags['tag_name'].head(10000))

cosine_sim_tag = linear_kernel(tfidf_matrix_tag, tfidf_matrix_tag)
print(cosine_sim_tag)

def tags_recom(title, n):    
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim_tag[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    book_indices = [i[0] for i in sim_scores]
    
    return list(titles.iloc[book_indices])

# list1=['Romeo and Juliet','The Hobbit']
def list_to_underscore_list(list_space):
    list_underscore=[]
    for i in list_space:
        j= '_'.join(i.split(' '))
        list_underscore.append(j)

    return list_underscore
    
def recom_list_tags(list1):
    for name in list1:
        recom=tags_recom(name, 10)
        list_out=list_to_underscore_list(recom)
        print (list_out)
    
recom_list_tags(list1)

auth_book_tags = book_tags.groupby('book_id')['tag_name'].apply(' '.join).reset_index()
print(auth_book_tags)

df_books = pd.merge(df_books, auth_book_tags,
                   left_on='book_id', right_on='book_id', how='inner')
print(df_books.head())

df_books['combined'] = pd.Series(df_books[['authors','tag_name']]
                                .fillna('').values.tolist()).str.join(' ')

tfidf_matrix_combined = tf.fit_transform(df_books['combined'])

cosine_sim_combined = linear_kernel(tfidf_matrix_combined,
                                    tfidf_matrix_combined)

print(cosine_sim_combined)

def combined_recom(title, n):    
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim_combined[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    book_indices = [i[0] for i in sim_scores]
    
    return list(titles.iloc[book_indices])

# list1=['Romeo and Juliet','The Hobbit']
def list_to_underscore_list(list_space):
    list_underscore=[]
    for i in list_space:
        j= '_'.join(i.split(' '))
        list_underscore.append(j)

    return list_underscore
    
def recom_list_combined(list1):
    for name in list1:
        recom=combined_recom(name, 10)
        list_out=list_to_underscore_list(recom)
        print (list_out)
    
recom_list_combined(list1)