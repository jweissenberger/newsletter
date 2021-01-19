from flask import (
    Flask,
    render_template,
    request
)
from flask_bootstrap import Bootstrap
import time

from hf_summarizer import pegasus_summarization, chunk_bart
from common import new_text_checker
from scraping import return_single_article, source_from_url
from statistical_summarize import run_tf_idf_summarization, run_word_frequency_summarization
from sentiment_analysis import hf_topn_sentiment

# Initialize App
app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def test():
    return render_template('article_input.html')


@app.route('/output')
def output():

    articles = [{'source': 'CNN', 'authors': 'Mr Author', 'title': 'Trump did a thing',
                 'pegasus': 'pegasus summary', 'bart': 'bart summary', 'tfidf': 'tfidf summary',
                 'word_frequency': 'wf summary', 'positive_sentences': ['positive sentence'],
                 'negative_sentences':['negative sentences']}
                ]
    return render_template('article_output.html', articles=articles)




@app.route('/generated_articles', methods=['GET', 'POST'])
def output_article_generation():

    if request.method == 'POST':

        # task = backgroud_article_generation.apply_async(input_data=request.form)
        input_data = request.form
        a = time.time()

        articles = []

        print('Pull Articles')
        # get articles
        for article_index in range(5):

            # if a link is given use newsarticle3k else parse the given text
            if input_data[f'link{article_index}']:
                try:
                    # TODO: check if its a link or just text
                    article = return_single_article(input_data[f'link{article_index}'], output_type='string')
                except:
                    source = source_from_url(input_data[f'link{article_index}'])
                    article = {'source': source, 'article': "Unable to pull article from this source"}
                    print("Failed to pull article from", source)

                print(f'Pulled from: {article["source"]}')
                articles.append(article)

        num_sentences = 6

        summaries = article_generator(articles=articles, num_sentences=num_sentences)

        b = time.time()

        total_time = (b - a) / 60

    return render_template('multi_analyze.html', total_time=total_time, summaries=summaries)


def article_generator(articles, num_sentences=7):
    """

    :param articles: list of dicts containing the articles
    :param num_sentences: number of the sentences for the statistical summarizers
    :return: list of dictionaries containing strings of each of the 4 summaries for each article in the list of articles
    """

    summaries = []
    for index, value in enumerate(articles):

        if value['article'] == "Unable to pull article from this source":
            summaries.append("Failed to pull article :( ")
            continue

        article = value

        print(value['source'], 'Pegasus Summary')
        summ = pegasus_summarization(text=value['article'], model_name='google/pegasus-cnn_dailymail')
        article['pegasus'] = new_text_checker(new_text=summ, orig_text=value['article'])

        print(value['source'], 'Bart Summary')
        summ = chunk_bart(value['article'])
        article['bart'] = new_text_checker(new_text=summ, orig_text=value['article'])

        print(value['source'], 'TF IDF')
        article['tfidf'] = run_tf_idf_summarization(value['article'], num_sentences)

        print(value['source'], 'Word Frequency')
        article['word_frequency'] = run_word_frequency_summarization(value['article'], num_sentences)

        print(value['source'], 'Sentiment Analysis')
        top_positive, top_negative = hf_topn_sentiment(value['article'])
        article['positive_sentences'] = top_positive
        article['negative_sentences'] = top_negative

        summaries.append(article)

    return summaries


@app.route('/article_generation')
def article_generation():
    return render_template('multi_article.html')


if __name__ == '__main__':
    app.run(debug=True)
