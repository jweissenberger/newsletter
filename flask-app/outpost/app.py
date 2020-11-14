from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import time

from hf_summarizer import chunk_summarize_t5, pegasus_summarization, chunk_bart
from common import sentence_tokenizer, plagiarism_checker, clean_text
from scraping import return_single_article, source_from_url
from statistical_summarize import run_tf_idf_summarization, run_word_frequency_summarization

# Initialize App
app = Flask(__name__)
Bootstrap(app)

VERSION = 'v0.1.4'


def generate_header(t5='', xsum='', multi='', plag='', ext='', generate=''):

    # need to set what you want to 'class="active"'
    header = f'<div class="jumbotron text-center"><div class="container">' \
             f'<h2>The Outpost News Article Analysis Tool {VERSION}</h2></div></div>'\
             f'<div class="topnav">' \
             f'<a {generate} href="/">Article Generation</a>' \
             f'<a {multi} href="/multi_news">Multi Article Summary</a>' \
             f'<a {xsum} href="/xsum">XSum Summary</a>' \
             f'<a {t5} href="/t5">T5 Summary</a>' \
             f'<a {plag} href="/plagiarism">Plagiarism Detection</a>' \
             f'<a {ext} href="/extract">Article Extraction</a>' \
             f'</div>'
    return header


@app.route('/extract')
def text_extraction():

    header = generate_header(ext='class="active"')  # update

    return render_template('extract.html', header=header, results='')


@app.route('/extract_results', methods=['GET', 'POST'])
def extraction_result():
    header = generate_header(ext='class="active"')

    if request.method == 'POST':
        link = request.form['article_link']

        output = return_single_article(link, output_type='html')

        results = output['article']
        summary = output['summary']

    return render_template('extract.html', header=header, results=results, summary=summary)


@app.route('/multi_news')
def multi_news_summarize():

    header = generate_header(multi='class="active"')  # update

    return render_template('multi_news_summarize.html', header=header, summarizer="Multi Article",
                           result_url='/multi_result')


@app.route('/multi_result', methods=['GET', 'POST'])
def multi_news_result():
    header = generate_header(multi='class="active"')

    if request.method == 'POST':
        texts = []
        orig_text = {}
        for i in range(4):
            temp = request.form[f'text{i+1}']
            orig_text[f'text{i+1}'] = temp
            texts.append(clean_text(temp))

        clean = ''
        for i in texts:
            clean += i + '\n||||\n'

        a = time.time()
        summary = pegasus_summarization(text=clean, model_name='google/pegasus-multi_news')
        b = time.time()
        summary_time = b-a

        output = plagiarism_checker(new_text=summary, orig_text=clean)

    return render_template('multi_news_summarize_result.html', header=header,
                           summary=output, time=summary_time, summarizer="Multi Article", **orig_text)


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

    header = generate_header(t5='class="active"')

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


@app.route('/generated_articles', methods=['GET', 'POST'])
def output_article_generation():
    header = generate_header(generate='class="active"')
    if request.method == 'POST':

        a = time.time()

        orig_text = {}
        left_articles = []
        right_articles = []
        center_articles = []

        print('Pull Articles')
        # get right and left articles, summaries
        for s in ['l', 'r', 'c']:
            if s == 'c':
                length = 2
            else:
                length = 5
            for i in range(length):

                orig_text[f'{s}_link{i+1}'] = request.form[f'{s}_link{i+1}']
                # if a link is given use newsarticle3k else parse the given text
                if orig_text[f'{s}_link{i+1}']:
                    try:
                        article = return_single_article(orig_text[f'{s}_link{i+1}'], output_type='string')
                    except:
                        source = source_from_url(orig_text[f'{s}_link{i+1}'])
                        article = {'source': source, 'article': "Unable to pull article from this source"}
                        print("Failed to pull article from", source)

                    print(f'Pulled from: {article["source"]}')
                    if s == 'l':
                        left_articles.append(article)
                    if s == 'r':
                        right_articles.append(article)
                    if s == 'c':
                        center_articles.append(article)


        num_sentences = int(request.form['num_sentences'])

        right_summaries = article_generator(articles=right_articles, num_sentences=num_sentences, article_type='Right')
        left_summaries = article_generator(articles=left_articles, num_sentences=num_sentences, article_type='Left')
        center_summaries = article_generator(articles=center_articles, num_sentences=num_sentences, article_type='Center')

        center_html = ''
        for i in center_summaries.keys():
            center_html += center_summaries[i] + "<br><br>"

        right_and_left_html = '<table style="margin-left:auto;margin-right:auto;">'

        max_articles = max(len(right_summaries.keys()), len(left_summaries.keys()))
        for i in range(max_articles):

            right_and_left_html += f'<tr><th style="text-align:center"><p style="font-size:20px">Left Article {i+1}</p></th>' \
                f'<th style="text-align:center"><p style="font-size:20px">Right Article {i+1}</p></th></tr>'

            right_and_left_html += '<tr><td><p>'

            if left_summaries.get(f'summary_{i}'):
                right_and_left_html += left_summaries[f'summary_{i}']
            else:
                right_and_left_html += ' '

            right_and_left_html += '</p></td><td><p>'

            if right_summaries.get(f'summary_{i}'):
                right_and_left_html += right_summaries[f'summary_{i}']
            else:
                right_and_left_html += ' '

            right_and_left_html += '</p></td></tr>'

        right_and_left_html += '</table>'

        b = time.time()

        total_time = (b-a)/60

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
    # TODO this should probably just be a list not a dictionary
    print(f"{article_type} Summaries")
    summaries = {}
    for index, value in enumerate(articles):

        if value['article'] == "Unable to pull article from this source":
            summaries[f'summary_{index}'] = "Failed to pull article :( "
            continue

        print(value['source'], 'TF IDF')
        summaries[f'summary_{index}'] = f"<b>{value['source']}</b>:<br><br>{run_tf_idf_summarization(value['article'], num_sentences)}<br><br>"

        print(value['source'], 'Word Frequency')
        summaries[f'summary_{index}'] += run_word_frequency_summarization(value['article'], num_sentences) + '<br><br>'

        print(value['source'], 'Bart Summary')
        sum = chunk_bart(value['article'])
        summaries[f'summary_{index}'] += plagiarism_checker(new_text=sum, orig_text=value['article']) + '<br><br>'

        print(value['source'], 'Pegasus Summary')
        sum = pegasus_summarization(text=value['article'], model_name='google/pegasus-cnn_dailymail')
        summaries[f'summary_{index}'] += plagiarism_checker(new_text=sum, orig_text=value['article']) + '<br><br>'

    return summaries

@app.route('/')
def article_generation():
    header = generate_header(generate='class="active"')
    return render_template('multi_article.html', header=header)


@app.route('/plagiarism')
def plagiarism():

    header = generate_header(plag='class="active"')

    return render_template('plagiarism.html', header=header, result='',
                           result_url='/t5_result')

@app.route('/plagiarism_result', methods=['GET', 'POST'])
def plagiarism_result():

    header = generate_header(plag='class="active"')

    if request.method == 'POST':
        orig = request.form['orig']
        orig = clean_text(orig)
        new = request.form['new']
        new = clean_text(new)

        result = plagiarism_checker(new_text=new, orig_text=orig)

    return render_template('plagiarism.html', header=header, result=result,
                           result_url='/t5_result')


if __name__ == '__main__':
    app.run(debug=True)
