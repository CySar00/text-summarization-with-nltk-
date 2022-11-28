import os, re, sys
import nltk
import  spacy
import heapq

nltk.download('punkt')
nltk.download('stopwords')

from flask import Flask, render_template, request
from nltk.corpus import stopwords

from spacy.lang.en.stop_words import STOP_WORDS


app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('Home.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    summary = ''
    if request.method == 'POST':
        my_file = request.form['myfile']
        if my_file:
            with open(my_file, "r", encoding="utf8") as f:
                article_text = f.read()
        else:
            article_text = request.form['text']

        # Remove \n, \t, square brackets and extra spaces
        article_text = re.sub(r'\n', ' ', article_text)
        article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
        article_text = re.sub(r'\s+', ' ', article_text)

        # Remove any special characters and digits
        formatted_article_text = re.sub('[^a-zA-z]', ' ', article_text)
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
        formatted_article_text = re.sub(r'\n', ' ', formatted_article_text)

        # print(formatted_article_text)

        # list of stopwords given by nltk
        stopwords = nltk.corpus.stopwords.words('english')

        #tokens = [_tok for _tok in nltk.word_tokenize(formatted_article_text.lower()) if _tok not in stopwords]
        tokens = [_tok for _tok in nltk.word_tokenize(formatted_article_text) if _tok not in stopwords]

        # count how many times each word occurs in the text
        word_count = {}
        for word in tokens:

            if word not in word_count.keys():
                word_count[word] = 1
            else:
                word_count[word] += 1

        max_word_count = max(word_count.values())

        # "normalize" the score by the max_word_count i.e. the value of the word which appeared the
        # max number of times
        for word in word_count.keys():
            word_count[word] = word_count[word] / max_word_count

        print(word_count)

        sentence_list = nltk.sent_tokenize(article_text)

        # find the score of each sentence
        # the score of each sentence is calculated by summing the partial scores of each word in the sentence
        sentence_score = {}
        for sentence in sentence_list:


            _toks = [_tok for _tok in nltk.word_tokenize(sentence.lower())]
            for _tok in _toks:
                if _tok in word_count.keys():
                    if len(sentence.split(' ')) < 30:

                        if sentence not in sentence_score:
                            sentence_score[sentence] = word_count[_tok]

                        else:
                            sentence_score[sentence] += word_count[_tok]

        # find the top n=7 sentences i.e. the sentences with the max scores
        top_sentences = heapq.nlargest(7, sentence_score, key = sentence_score.get)

        # concatenate the top sentences
        summary = ' '.join(top_sentences)

























    return render_template('Result.html', summary=summary)


if __name__ == '__main__':
    app.run(debug=True)
