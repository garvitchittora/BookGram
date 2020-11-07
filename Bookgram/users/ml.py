import os
import sys
import numpy as np
import pandas as pd
import sklearn
import warnings
warnings.filterwarnings('ignore')

from scipy import stats
from scipy.stats import pearsonr
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import linear_kernel
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import RegexpTokenizer
import re
from io import BytesIO
from collections import Counter


df_ratings = pd.read_csv('../input/goodbooks-10k/ratings.csv')
df_books = pd.read_csv('../input/goodbooks-10k/books.csv')
book_tags = pd.read_csv('../input/goodbooks-10k/book_tags.csv')
tags = pd.read_csv('../input/goodbooks-10k/tags.csv')
tag_books = book_tags
books_df = df_books

merge_tags = pd.merge(book_tags, tags, left_on='tag_id',
                      right_on='tag_id', how='inner')

titles = df_books['title']
indices = pd.Series(df_books.index, index=df_books['title'])

tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),
                     min_df=0, stop_words='english')

def list_to_underscore_list(list_space):
    list_underscore=[]
    for i in list_space:
        j= '_'.join(i.split(' '))
        list_underscore.append(j)

    return list_underscore



def content_auth():
    tfidf_matrix_auth = tf.fit_transform(df_books['authors'])
    cosine_sim_auth = linear_kernel(tfidf_matrix_auth, tfidf_matrix_auth)
    return cosine_sim_auth


def authors_recom(title, n):
    cos=content_auth()
    idx = indices[title]
    sim_scores = list(enumerate(cos[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    book_indices = [i[0] for i in sim_scores]
    
    return list(titles.iloc[book_indices])

    
def recom_list_auth(list1):
    for name in list1:
        recom=authors_recom(name, 10)
        list_out=list_to_underscore_list(recom)
        print (list_out)

        
book_tags = pd.merge(df_books, merge_tags, left_on='book_id',
                     right_on='goodreads_book_id', how='inner')

def content_tags():
    tfidf_matrix_tag = tf.fit_transform(book_tags['tag_name'].head(10000))
    cosine_sim_tag = linear_kernel(tfidf_matrix_tag, tfidf_matrix_tag)
    return cosine_sim_tag

def tags_recom(title, n):
    cos=content_tags()
    idx = indices[title]
    sim_scores = list(enumerate(cos[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    book_indices = [i[0] for i in sim_scores]
    
    return list(titles.iloc[book_indices])

    
def recom_list_tags(list1):
    for name in list1:
        recom=tags_recom(name, 10)
        list_out=list_to_underscore_list(recom)
        print (list_out)
        
        
auth_book_tags = book_tags.groupby('book_id')['tag_name'].apply(' '.join).reset_index()

books_df = pd.merge(df_books, auth_book_tags,
                   left_on='book_id', right_on='book_id', how='inner')

books_df['combined'] = pd.Series(books_df[['authors','tag_name']]
                                .fillna('').values.tolist()).str.join(' ')


def content_combined():
    tfidf_matrix_combined = tf.fit_transform(books_df['combined'])

    cosine_sim_combined = linear_kernel(tfidf_matrix_combined,
                                        tfidf_matrix_combined)
    return cosine_sim_combined


def combined_recom(title, n):
    cos=content_combined()
    idx = indices[title]
    sim_scores = list(enumerate(cos[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]
    book_indices = [i[0] for i in sim_scores]
    
    return list(titles.iloc[book_indices])

    
def recom_list_combined(list1):
    for name in list1:
        recom=combined_recom(name, 10)
        list_out=list_to_underscore_list(recom)
        print (list_out)
        
