from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import flair
import random

from subjectivity_analysis import textblob_topn_subjectivity
from sentiment_analysis import flair_topn_sentiment
from hft5_summarizer import chunk_summarize_t5
from common import sentence_tokenizer


# Initialize App
app = Flask(__name__)
Bootstrap(app)

VERSION = 'v0.0.5'


def clean_text(text):
    # TODO move to common

    text = text.replace('&', 'and')

    allowed_symbols = ['"', "'", ' ', '$', ':', '.', '?', '!', '(', ')', '/', ';']

    new_text = ""
    for char in text:
        if char.isalnum() or char in allowed_symbols:
            new_text += char

    return new_text


def generate_header(summarizer='', single='', multi=''):

    # need to set what you want to 'class="active"'
    header = f'<div class="jumbotron text-center"><div class="container">' \
             f'<h2>The Outpost News Article Analysis Tool {VERSION}</h2></div></div>'\
             f'<div class="topnav">' \
             f'<a {multi} href="/">Multi Article Analysis</a>' \
             f'<a {single} href="/single">Single Article Analysis</a>' \
             f'<a {summarizer} href="/sum">Summarizer</a>' \
             f'</div>'
    return header


@app.route('/sum')
def summarize():

    header = generate_header(summarizer='class="active"')

    return render_template('summarize.html', version=VERSION, header=header)


@app.route('/summarize_result', methods=['GET', 'POST'])
def summarize_result():
    header = generate_header(summarizer='class="active"')

    if request.method == 'POST':
        rawtext = request.form['rawtext']
        clean = clean_text(rawtext)

        large_summary = chunk_summarize_t5(clean, size='large')

    return render_template('summarize_result.html', version=VERSION, header=header, rawtext=rawtext,
                           large_summary=large_summary)


@app.route('/single')
def single():
    header = generate_header(single='class="active"')
    return render_template('single.html', version=VERSION, header=header)


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    header = generate_header(single='class="active"')
    if request.method == 'POST':
        rawtext = request.form['rawtext']

        rawtext = clean_text(rawtext)

        summary = chunk_summarize_t5(rawtext)

        most_subjective, least_subjective = textblob_topn_subjectivity(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))

        top_positive, top_negative = flair_topn_sentiment(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))

    return render_template('analyze.html', version=VERSION, header=header, summary=summary,
                           most_subjective=most_subjective, least_subjective=least_subjective,
                           top_positive=top_positive, top_negative=top_negative)


@app.route('/multi_analyze', methods=['GET', 'POST'])
def multi_analyze():
    header = generate_header(multi='class="active"')
    if request.method == 'POST':

        orig_text = {}
        for i in range(5):
            orig_text[f'l_source{i+1}'] = request.form[f'l_source{i+1}']
            orig_text[f'l_text{i+1}'] = request.form[f'l_text{i+1}']
            orig_text[f'r_source{i + 1}'] = request.form[f'r_source{i + 1}']
            orig_text[f'r_text{i + 1}'] = request.form[f'r_text{i + 1}']

        cleaned_text = {}
        for i in range(5):
            cleaned_text[f'l_text{i+1}'] = clean_text(orig_text[f'l_text{i+1}'])
            cleaned_text[f'r_text{i + 1}'] = clean_text(orig_text[f'r_text{i + 1}'])

        num_subj_sent_sentences = int(request.form['num_subj_sent_sentences'])

        # import it once so you don't have to load bert 10 times
        model = flair.models.TextClassifier.load('en-sentiment')

        left_positive = []
        left_negative = []

        right_positive = []
        right_negative = []

        individual_article_results = {}
        for i in range(5):

            if cleaned_text[f'l_text{i+1}']:
                individual_article_results[f'summary_l{i+1}'] = chunk_summarize_t5(cleaned_text[f'l_text{i+1}'])

                most_subjective, least_subjective = textblob_topn_subjectivity(cleaned_text[f'l_text{i+1}'], num_sentences=num_subj_sent_sentences)
                individual_article_results[f'most_subjective_l{i+1}'] = most_subjective
                individual_article_results[f'least_subjective_l{i + 1}'] = least_subjective

                top_positive, top_negative = flair_topn_sentiment(cleaned_text[f'l_text{i+1}'], model=model, num_sentences=num_subj_sent_sentences)
                individual_article_results[f'top_positive_l{i+1}'] = reversed(top_positive)
                individual_article_results[f'top_negative_l{i + 1}'] = reversed(top_negative)
                left_positive.extend(top_positive)
                left_negative.extend(top_negative)

            if cleaned_text[f'r_text{i+1}']:
                individual_article_results[f'summary_r{i+1}'] = chunk_summarize_t5(cleaned_text[f'r_text{i+1}'])

                most_subjective, least_subjective = textblob_topn_subjectivity(cleaned_text[f'r_text{i+1}'], num_sentences=num_subj_sent_sentences)
                individual_article_results[f'most_subjective_r{i+1}'] = most_subjective
                individual_article_results[f'least_subjective_r{i + 1}'] = least_subjective

                top_positive, top_negative = flair_topn_sentiment(cleaned_text[f'r_text{i+1}'], model=model, num_sentences=num_subj_sent_sentences)
                individual_article_results[f'top_positive_r{i+1}'] = reversed(top_positive)
                individual_article_results[f'top_negative_r{i + 1}'] = reversed(top_negative)
                right_positive.extend(top_positive)
                right_negative.extend(top_negative)

        # get the most positive and negative sentences from both sides
        left_positive = sorted(left_positive, key=lambda x: x[0])
        left_positive = reversed(left_positive[-num_subj_sent_sentences:])

        right_positive = sorted(right_positive, key=lambda x: x[0])
        right_positive = reversed(right_positive[-num_subj_sent_sentences:])

        left_negative = sorted(left_negative, key=lambda x: x[0])
        left_negative = reversed(left_negative[-num_subj_sent_sentences:])

        right_negative = sorted(right_negative, key=lambda x: x[0])
        right_negative = reversed(right_negative[-num_subj_sent_sentences:])

        # generate right left and overall summaries
        left_summary = []
        right_summary = []
        for i in range(5):
            if individual_article_results[f'summary_l{i+1}']:
                left_summary.append(individual_article_results[f'summary_l{i+1}'])
            if individual_article_results[f'summary_r{i+1}']:
                right_summary.append(individual_article_results[f'summary_r{i + 1}'])

        left_summary = random.shuffle(left_summary)
        right_summary = random.shuffle(right_summary)

        new_summary = ''
        for i in left_summary:
            new_summary += i + ' '
        left_summary = new_summary

        new_summary = ''
        for i in right_summary:
            new_summary += i + ' '
        right_summary = new_summary

        if len(sentence_tokenizer(left_summary)) > 7:
            left_summary = chunk_summarize_t5(left_summary)

        if len(sentence_tokenizer(right_summary)) > 7:
            right_summary = chunk_summarize_t5(right_summary)

        overall_summary = chunk_summarize_t5(left_summary + right_summary)

    return render_template('multi_analyze.html', version=VERSION, header=header,
                           left_positive=left_positive, left_negative=left_negative,
                           right_positive=right_positive, right_negative=right_negative,
                           num_subj_sent_sentences=num_subj_sent_sentences,
                           left_summary=left_summary, right_summary=right_summary, overall_summary=overall_summary,
                           **orig_text, **individual_article_results)


@app.route('/')
def multi_article():
    header = generate_header(multi='class="active"')
    return render_template('multi_article.html', version=VERSION, header=header)


if __name__ == '__main__':
    app.run(debug=True)
