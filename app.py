# app.py
from __future__ import unicode_literals
from flask import Flask,render_template,url_for,request, session
from flask import *

import time
import spacy
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from datetime import date
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
# Import Heapq for Finding the Top N Sentences
from heapq import nlargest

nlp = spacy.load('en_core_web_sm')
app = Flask(__name__)


def text_summarizer(raw_docx):
    raw_text = raw_docx
    docx = nlp(raw_text)
    stopwords = list(STOP_WORDS)
    # Build Word Frequency # word.text is tokenization in spacy
    word_frequencies = {}  
    for word in docx:  
        if word.text not in stopwords:
            if word.text not in word_frequencies.keys():
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1


    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():  
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
    # Sentence Tokens
    sentence_list = [ sentence for sentence in docx.sents ]

    # Sentence Scores
    sentence_scores = {}  
    for sent in sentence_list:  
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if len(sent.text.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_frequencies[word.text.lower()]


    summarized_sentences = nlargest(7, sentence_scores, key=sentence_scores.get)
    final_sentences = [ w.text for w in summarized_sentences ]
    summary = ' '.join(final_sentences)
    return summary



def readingTime(mytext):
    
    total_words = len([ token.text for token in nlp(mytext)])
    estimatedTime = total_words/200.0
    return estimatedTime


@app.route('/')
def index():
    return render_template('index.html')




def get_text(url):
    req = Request(url,headers={'User-Agent' : "Magic Browser"})
    page = urlopen(req)
    soup = BeautifulSoup(page)
    fetched_text = ' '.join(map(lambda p:p.text,soup.find_all('p')))
    return fetched_text


@app.route('/process',methods=['GET','POST'])
def analyze():
	start = time.time()

	if request.method == 'POST':

		rawtext = request.form['input_text']
		final_reading_time = readingTime(rawtext)
		final_summary = text_summarizer(rawtext)
		summary_reading_time = readingTime(final_summary)
		end = time.time()
		final_time = end-start
	return render_template('result.html',ctext=rawtext,final_summary=final_summary,final_time=final_time,final_reading_time=final_reading_time,summary_reading_time=summary_reading_time)
	

@app.route('/process_url',methods=['GET','POST'])
def process_url():
    start = time.time()
    if request.method == 'POST':
        input_url = request.form['input_url']
        raw_text = get_text(input_url)
        final_reading_time = readingTime(raw_text)
        final_summary = text_summarizer(raw_text)
        summary_reading_time = readingTime(final_summary)
        end = time.time()
        final_time = end-start
    return render_template('result.html',ctext=raw_text,
                        final_summary=final_summary,
                        final_time=final_time,
                        final_reading_time=final_reading_time,
                        summary_reading_time=summary_reading_time)



if __name__ == '__main__':
	app.run(debug=True)
    
    
    
    
    
    
    
