from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import flair
import random
import time

from subjectivity_analysis import textblob_topn_subjectivity
from sentiment_analysis import flair_topn_sentiment
from hf_summarizer import chunk_summarize_t5, pegasus_summarization
from common import sentence_tokenizer, plagiarism_checker, clean_text


# Initialize App
app = Flask(__name__)
Bootstrap(app)

VERSION = 'v0.0.9'


def generate_header(t5='', xsum='', multi=''):

    # need to set what you want to 'class="active"'
    header = f'<div class="jumbotron text-center"><div class="container">' \
             f'<h2>The Outpost News Article Analysis Tool {VERSION}</h2></div></div>'\
             f'<div class="topnav">' \
             f'<a {multi} href="/">Multi Article Summary</a>' \
             f'<a {xsum} href="/xsum">XSum Summary</a>' \
             f'<a {t5} href="/t5">T5</a>' \
             f'</div>'
    return header


@app.route('/')
def multi_news_summarize():

    header = generate_header(multi='class="active"')  # update

    return render_template('summarize.html', header=header, summarizer="Multi Article",
                           result_url='/multi_result')


@app.route('/multi_result', methods=['GET', 'POST'])
def multi_news_result():
    header = generate_header(multi='class="active"')

    if request.method == 'POST':
        rawtext = request.form['rawtext']
        clean = clean_text(rawtext)

        a = time.time()
        summary = pegasus_summarization(text=clean, model_name='google/pegasus-multi_news')
        b = time.time()
        summary_time = b-a

        output = plagiarism_checker(new_text=summary, orig_text=clean)

    return render_template('summarize_result.html', header=header, rawtext=rawtext,
                           summary=output, time=summary_time, summarizer="Xsum")


@app.route('/xsum')
def xsum_summarize():

    header = generate_header(xsum='class="active"')  # update

    return render_template('summarize.html', header=header, summarizer="Xsum",
                           result_url='/xsum_result')


@app.route('/xsum_result', methods=['GET', 'POST'])
def xsum_result():
    header = generate_header(xsum='class="active"')

    if request.method == 'POST':
        rawtext = request.form['rawtext']
        clean = clean_text(rawtext)

        a = time.time()
        summary = pegasus_summarization(text=clean, model_name='google/pegasus-xsum')
        b = time.time()
        summary_time = b-a

        output = plagiarism_checker(new_text=summary, orig_text=clean)

    return render_template('summarize_result.html', header=header, rawtext=rawtext,
                           summary=output, time=summary_time, summarizer="Xsum")

@app.route('/t5')
def t5_summarize():

    header = generate_header(t5='class="active"')  # update

    return render_template('summarize.html', header=header, summarizer="T5",
                           result_url='/t5_result')


@app.route('/t5_result', methods=['GET', 'POST'])
def t5_result():
    header = generate_header(t5='class="active"')

    if request.method == 'POST':
        rawtext = request.form['rawtext']
        clean = clean_text(rawtext)

        a = time.time()
        summary = chunk_summarize_t5(clean, size='large')
        b = time.time()
        summary_time = b-a

        output = plagiarism_checker(new_text=summary, orig_text=clean)

    return render_template('summarize_result.html', header=header, rawtext=rawtext,
                           summary=output, time=summary_time, summarizer="T5")


# @app.route('/multi_news_result', methods=['GET', 'POST'])
# def summarize_result():
#     header = generate_header(summarizer='class="active"')
#
#     if request.method == 'POST':
#         rawtext = request.form['rawtext']
#         clean = clean_text(rawtext)
#
#         times = {}
#
#         a = time.time()
#         summary = chunk_summarize_t5(clean, size='large')
#         b = time.time()
#         times['t5_time'] = b-a
#
#         large_summary = plagiarism_checker(new_text=summary, orig_text=clean)
#
#         # pegasus models
#         models = ['google/pegasus-xsum', 'google/pegasus-multi_news']
#         pegasus_models = {}
#         for model in models:
#             model_name = model.split('-')[-1]
#
#             a = time.time()
#             summary = pegasus_summarization(text=clean, model_name=model)
#             b = time.time()
#             times[f'{model_name}_time'] = b-a
#
#             output = plagiarism_checker(new_text=summary, orig_text=clean)
#             pegasus_models[model_name] = output
#
#     return render_template('summarize_result.html', header=header, rawtext=rawtext,
#                            large_summary=large_summary, **pegasus_models, **times)
#
#
# @app.route('/summarize_result', methods=['GET', 'POST'])
# def summarize_result():
#     header = generate_header(summarizer='class="active"')
#
#     if request.method == 'POST':
#         rawtext = request.form['rawtext']
#         clean = clean_text(rawtext)
#
#         times = {}
#
#         a = time.time()
#         summary = chunk_summarize_t5(clean, size='large')
#         b = time.time()
#         times['t5_time'] = b-a
#
#         large_summary = plagiarism_checker(new_text=summary, orig_text=clean)
#
#         # pegasus models
#         models = ['google/pegasus-xsum', 'google/pegasus-multi_news']
#         pegasus_models = {}
#         for model in models:
#             model_name = model.split('-')[-1]
#
#             a = time.time()
#             summary = pegasus_summarization(text=clean, model_name=model)
#             b = time.time()
#             times[f'{model_name}_time'] = b-a
#
#             output = plagiarism_checker(new_text=summary, orig_text=clean)
#             pegasus_models[model_name] = output
#
#     return render_template('summarize_result.html', header=header, rawtext=rawtext,
#                            large_summary=large_summary, **pegasus_models, **times)
#
#
# @app.route('/single')
# def single():
#     header = generate_header(single='class="active"')
#     return render_template('single.html', header=header)
#
#
# @app.route('/analyze', methods=['GET', 'POST'])
# def analyze():
#     header = generate_header(single='class="active"')
#     if request.method == 'POST':
#         rawtext = request.form['rawtext']
#
#         rawtext = clean_text(rawtext)
#
#         summary = chunk_summarize_t5(rawtext)
#
#         most_subjective, least_subjective = textblob_topn_subjectivity(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))
#
#         top_positive, top_negative = flair_topn_sentiment(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))
#
#     return render_template('analyze.html', header=header, summary=summary,
#                            most_subjective=most_subjective, least_subjective=least_subjective,
#                            top_positive=top_positive, top_negative=top_negative)
#
#
# @app.route('/multi_analyze', methods=['GET', 'POST'])
# def multi_analyze():
#     header = generate_header(multi='class="active"')
#     if request.method == 'POST':
#
#         orig_text = {}
#         for i in range(5):
#             orig_text[f'l_source{i+1}'] = request.form[f'l_source{i+1}']
#             orig_text[f'l_text{i+1}'] = request.form[f'l_text{i+1}']
#             orig_text[f'r_source{i + 1}'] = request.form[f'r_source{i + 1}']
#             orig_text[f'r_text{i + 1}'] = request.form[f'r_text{i + 1}']
#
#         cleaned_text = {}
#         for i in range(5):
#             cleaned_text[f'l_text{i+1}'] = clean_text(orig_text[f'l_text{i+1}'])
#             cleaned_text[f'r_text{i + 1}'] = clean_text(orig_text[f'r_text{i + 1}'])
#
#         num_subj_sent_sentences = int(request.form['num_subj_sent_sentences'])
#
#         # import it once so you don't have to load bert 10 times
#         model = flair.models.TextClassifier.load('en-sentiment')
#
#         left_positive = []
#         left_negative = []
#
#         right_positive = []
#         right_negative = []
#
#         individual_article_results = {}
#         for i in range(5):
#
#             if cleaned_text[f'l_text{i+1}']:
#                 individual_article_results[f'summary_l{i+1}'] = chunk_summarize_t5(cleaned_text[f'l_text{i+1}'])
#
#                 most_subjective, least_subjective = textblob_topn_subjectivity(cleaned_text[f'l_text{i+1}'], num_sentences=num_subj_sent_sentences)
#                 individual_article_results[f'most_subjective_l{i+1}'] = most_subjective
#                 individual_article_results[f'least_subjective_l{i + 1}'] = least_subjective
#
#                 top_positive, top_negative = flair_topn_sentiment(cleaned_text[f'l_text{i+1}'], model=model, num_sentences=num_subj_sent_sentences)
#                 individual_article_results[f'top_positive_l{i+1}'] = reversed(top_positive)
#                 individual_article_results[f'top_negative_l{i + 1}'] = reversed(top_negative)
#                 left_positive.extend(top_positive)
#                 left_negative.extend(top_negative)
#
#             if cleaned_text[f'r_text{i+1}']:
#                 individual_article_results[f'summary_r{i+1}'] = chunk_summarize_t5(cleaned_text[f'r_text{i+1}'])
#
#                 most_subjective, least_subjective = textblob_topn_subjectivity(cleaned_text[f'r_text{i+1}'], num_sentences=num_subj_sent_sentences)
#                 individual_article_results[f'most_subjective_r{i+1}'] = most_subjective
#                 individual_article_results[f'least_subjective_r{i + 1}'] = least_subjective
#
#                 top_positive, top_negative = flair_topn_sentiment(cleaned_text[f'r_text{i+1}'], model=model, num_sentences=num_subj_sent_sentences)
#                 individual_article_results[f'top_positive_r{i+1}'] = reversed(top_positive)
#                 individual_article_results[f'top_negative_r{i + 1}'] = reversed(top_negative)
#                 right_positive.extend(top_positive)
#                 right_negative.extend(top_negative)
#
#         # get the most positive and negative sentences from both sides
#         left_positive = sorted(left_positive, key=lambda x: x[0])
#         left_positive = reversed(left_positive[-num_subj_sent_sentences:])
#
#         right_positive = sorted(right_positive, key=lambda x: x[0])
#         right_positive = reversed(right_positive[-num_subj_sent_sentences:])
#
#         left_negative = sorted(left_negative, key=lambda x: x[0])
#         left_negative = reversed(left_negative[-num_subj_sent_sentences:])
#
#         right_negative = sorted(right_negative, key=lambda x: x[0])
#         right_negative = reversed(right_negative[-num_subj_sent_sentences:])
#
#         # generate right left and overall summaries
#         left_summary = []
#         right_summary = []
#         for i in range(5):
#             if individual_article_results.get(f'summary_l{i+1}'):
#                 left_summary.append(individual_article_results[f'summary_l{i+1}'])
#             if individual_article_results.get(f'summary_r{i+1}'):
#                 right_summary.append(individual_article_results[f'summary_r{i + 1}'])
#
#         random.shuffle(left_summary)
#         random.shuffle(right_summary)
#
#         new_summary = ''
#         for i in left_summary:
#             new_summary += i + ' '
#         left_summary = new_summary
#
#         new_summary = ''
#         for i in right_summary:
#             new_summary += i + ' '
#         right_summary = new_summary
#
#         if len(sentence_tokenizer(left_summary)) > 7:
#             left_summary = chunk_summarize_t5(left_summary)
#
#         if len(sentence_tokenizer(right_summary)) > 7:
#             right_summary = chunk_summarize_t5(right_summary)
#
#         overall_summary = chunk_summarize_t5(left_summary + right_summary)
#
#     return render_template('multi_analyze.html', header=header,
#                            left_positive=left_positive, left_negative=left_negative,
#                            right_positive=right_positive, right_negative=right_negative,
#                            num_subj_sent_sentences=num_subj_sent_sentences,
#                            left_summary=left_summary, right_summary=right_summary, overall_summary=overall_summary,
#                            **orig_text, **individual_article_results)
#
#
# @app.route('/')
# def multi_article():
#     header = generate_header(multi='class="active"')
#     return render_template('multi_article.html', header=header)


if __name__ == '__main__':
    app.run(debug=True)
