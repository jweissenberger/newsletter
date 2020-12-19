from flask import (
    Flask,
    render_template,
    request
)
from flask_bootstrap import Bootstrap
from celery import Celery
import time

from hf_summarizer import pegasus_summarization, chunk_bart
from common import new_text_checker
from scraping import return_single_article, source_from_url
from statistical_summarize import run_tf_idf_summarization, run_word_frequency_summarization
from sentiment_analysis import hf_topn_sentiment

# Initialize App
app = Flask(__name__)
Bootstrap(app)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

VERSION = 'v0.1.6'


def generate_header():

    # need to set what you want to 'class="active"'
    header = f'<div class="jumbotron text-center"><div class="container">' \
             f'<h2>Newsletter {VERSION}</h2></div></div>'
    return header


@celery.task(bind=True)
def backgroud_article_generation(self, input_data):


    self.update_state(state='PROGRESS',
                      meta={'article': i, 'total': total,
                      'status': message})

    """
    render_template('multi_analyze.html', header=header, total_time=total_time, center_html=center_html,
                           right_and_left_html=right_and_left_html
                           )
    
    """

    return {'article': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@app.route('/generated_articles', methods=['GET', 'POST'])
def output_article_generation():
    header = generate_header()
    if request.method == 'POST':

        # task = backgroud_article_generation.apply_async(input_data=request.form)
        input_data = request.form
        a = time.time()

        articles = []

        print('Pull Articles')
        # get articles
        for article_index in range():

            orig_text[f'{s}_link{i + 1}'] = input_data[f'{s}_link{i + 1}']
            # if a link is given use newsarticle3k else parse the given text
            if orig_text[f'{s}_link{i + 1}']:
                try:
                    article = return_single_article(orig_text[f'{s}_link{i + 1}'], output_type='string')
                except:
                    source = source_from_url(orig_text[f'{s}_link{i + 1}'])
                    article = {'source': source, 'article': "Unable to pull article from this source"}
                    print("Failed to pull article from", source)

                print(f'Pulled from: {article["source"]}')
                if s == 'l':
                    left_articles.append(article)
                if s == 'r':
                    right_articles.append(article)
                if s == 'c':
                    center_articles.append(article)

        num_sentences = 6

        right_summaries = article_generator(articles=right_articles, num_sentences=num_sentences, article_type='Right')
        left_summaries = article_generator(articles=left_articles, num_sentences=num_sentences, article_type='Left')
        center_summaries = article_generator(articles=center_articles, num_sentences=num_sentences,
                                             article_type='Center')

        center_html = ''
        for i in range(len(center_summaries)):
            center_html += center_summaries[i] + "<br><br>"

        right_and_left_html = '<table style="margin-left:auto;margin-right:auto;">'

        max_articles = max(len(right_summaries), len(left_summaries))
        for i in range(max_articles):

            right_and_left_html += f'<tr><th style="text-align:center"><p style="font-size:20px">Left Article {i + 1}</p></th>' \
                f'<th style="text-align:center"><p style="font-size:20px">Right Article {i + 1}</p></th></tr>'

            right_and_left_html += '<tr><td><p>'

            if left_summaries and i < len(left_summaries):
                right_and_left_html += left_summaries[i]
            else:
                right_and_left_html += ' '

            right_and_left_html += '</p></td><td><p>'

            if right_summaries and i < len(right_summaries):
                right_and_left_html += right_summaries[i]
            else:
                right_and_left_html += ' '

            right_and_left_html += '</p></td></tr>'

        right_and_left_html += '</table>'

        b = time.time()

        total_time = (b - a) / 60

    return render_template('multi_analyze.html', header=header, total_time=total_time, center_html=center_html,
                           right_and_left_html=right_and_left_html
                           )


def article_generator(articles, num_sentences=7, article_type='Central'):
    """

    :param articles: list of dicts containing the articles
    :param num_sentences: number of the sentences for the statistical summarizers
    :param article_type: string:  Left, Right or Central
    :return: Dictionary containing strings of each of the 4 summaries for each article in the list of articles
    """

    print(f"{article_type} Summaries")
    summaries = []
    for index, value in enumerate(articles):

        if value['article'] == "Unable to pull article from this source":
            summaries.append("Failed to pull article :( ")
            continue

        print(value['source'], 'Pegasus Summary')
        summ = pegasus_summarization(text=value['article'], model_name='google/pegasus-cnn_dailymail')

        summaries.append(f"<b>{value['source']}</b>:<br><br>"
                         f"Link: {value['url']}<br><br>"
                         f"Author(s): {value['authors']}<br><br>"
                         f"{new_text_checker(new_text=summ, orig_text=value['article'])}<br><br>"
                         )

        print(value['source'], 'Bart Summary')
        summ = chunk_bart(value['article'])
        summaries[-1] += new_text_checker(new_text=summ, orig_text=value['article']) + '<br><br>'

        print(value['source'], 'TF IDF')
        summaries[-1] += f"{run_tf_idf_summarization(value['article'], num_sentences)}<br><br>"

        print(value['source'], 'Word Frequency')
        summaries[-1] += run_word_frequency_summarization(value['article'], num_sentences) + '<br><br>'

        print(value['source'], 'Sentiment Analysis')
        top_positive, top_negative = hf_topn_sentiment(value['article'])
        summaries[-1] += "Most Positive Sentences:<br>"
        for i in top_positive:
            summaries[-1] += i[1] + "<br>"

        summaries[-1] += "<br><br>Most Negative Sentences:<br>"
        for i in top_negative:
            summaries[-1] += i[1] + "<br>"

    return summaries


@app.route('/article_generation')
def article_generation():
    header = generate_header()
    return render_template('multi_article.html', header=header)


if __name__ == '__main__':
    app.run(debug=True)
