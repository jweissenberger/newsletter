from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import time
import math
import random

from hf_summarizer import chunk_summarize_t5, pegasus_summarization
from common import sentence_tokenizer, plagiarism_checker, clean_text
from scraping import return_single_article
from statistical_summarize import run_tf_idf_summarization

# Initialize App
app = Flask(__name__)
Bootstrap(app)

VERSION = 'v0.1.1'


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
def multi_analyze():
    header = generate_header(generate='class="active"')
    if request.method == 'POST':
        a = time.time()

        orig_text = {}
        left_articles = []
        right_articles = []

        print('Pull Articles')
        # get right and left articles, summaries
        for s in ['l', 'r']:
            for i in range(5):

                orig_text[f'{s}_link{i+1}'] = request.form[f'{s}_link{i+1}']
                # if a link is given use newsarticle3k else parse the given text
                if orig_text[f'{s}_link{i+1}']:
                    article = return_single_article(orig_text[f'{s}_link{i+1}'], output_type='string')
                    print(f'Pulled from: {article["source"]}')
                    if s == 'l':
                        left_articles.append(article)
                    else:
                        right_articles.append(article)

        assert len(left_articles) >= 1 and len(right_articles) >= 1, "Must have a least one article from each side"

        overall_text = ''
        for i in range(len(left_articles)):
            overall_text += ' \n ' + left_articles[i]['article']
        for i in range(len(right_articles)):
            overall_text += ' \n ' + right_articles[i]['article']

        print('Generating left and right summaries')
        print('Pass two summaries at a time into multi news')
        print("Right Summary")
        right_summary1 = ''
        for i in range(math.ceil(len(right_articles)/2)):
            if i*2 + 1 < len(right_articles):
                right_summary1 += ' \n ' + pegasus_summarization(
                    text=right_articles[i * 2]['summary'] + ' |||| ' + right_articles[i*2 + 1],
                    model_name='google/pegasus-multi_news'
                )
            else:
                right_summary1 += ' \n ' + pegasus_summarization(
                    text=right_articles[i * 2]['summary'],
                    model_name='google/pegasus-multi_news'
                )

        print("Left Summary")
        left_summary1 = ''
        for i in range(math.ceil(len(left_articles) / 2)):
            if i * 2 + 1 < len(left_articles):
                left_summary1 += ' \n ' + pegasus_summarization(
                    text=left_articles[i * 2]['summary'] + ' |||| ' + left_articles[i * 2 + 1],
                    model_name='google/pegasus-multi_news'
                )
            else:
                left_summary1 += ' \n ' + pegasus_summarization(
                    text=left_articles[i * 2]['summary'],
                    model_name='google/pegasus-multi_news'
                )

        left_summary1 = plagiarism_checker(new_text=left_summary1, orig_text=overall_text)
        right_summary1 = plagiarism_checker(new_text=right_summary1, orig_text=overall_text)

        print('Pass each article individually into multi news')
        left_sums = []
        left_summary3 = ''
        for i in range(len(left_articles)):
            print(f'Left article {i}')
            summ = ' \n ' + left_articles[i]['source'] + ': ' + pegasus_summarization(
                text=left_articles[i]['article'],
                model_name='google/pegasus-multi_news'
            )
            left_sums.append(summ)
            left_summary3 += summ

        right_sums = []
        right_summary3 = ''
        for i in range(len(right_articles)):
            print(f'Right article {i}')
            summ = ' \n ' + right_articles[i]['source'] + ': ' + pegasus_summarization(
                text=right_articles[i]['article'],
                model_name='google/pegasus-multi_news'
            )

            right_sums.append(summ)
            right_summary3 += summ

        right_summary3 = plagiarism_checker(new_text=right_summary3, orig_text=overall_text)
        left_summary3 = plagiarism_checker(new_text=left_summary3, orig_text=overall_text)

        print('Generate overall summaries')
        print('Summary 1')
        overall_summary1 = chunk_summarize_t5(left_summary1 + ' ' + right_summary1, size='large')
        overall_summary1 = plagiarism_checker(new_text=overall_summary1, orig_text=overall_text)

        print('Summary 2')
        if min(len(right_articles), len(left_articles)) > 2:
            # randomly choose two from each side to summarize
            text_to_summarize = ''
            for i in range(2):
                art1 = random.choice(right_sums)
                right_sums.remove(art1)
                art2 = random.choice(left_sums)
                left_sums.remove(art2)
                text_to_summarize += art1 + ' |||| ' + art2 + ' |||| '
                overall_summary3 = pegasus_summarization(
                    text=text_to_summarize,
                    model_name='google/pegasus-multi_news'
                )

        else:
            # randomly choose one from each side to summarize together
            art1 = random.choice(right_sums)
            art2 = random.choice(left_sums)
            text_to_summarize = art1 + ' |||| ' + art2 + ' |||| '
            overall_summary3 = pegasus_summarization(
                    text=text_to_summarize,
                    model_name='google/pegasus-multi_news'
                )
        overall_summary3 = plagiarism_checker(new_text=overall_summary3, orig_text=overall_text)

        b = time.time()

        total_time = (b-a)/60

    return render_template('multi_analyze.html', header=header, left_summary1=left_summary1,
                           left_summary3=left_summary3, right_summary1=right_summary1,
                           right_summary3=right_summary3, overall_summary1=overall_summary1,
                           overall_summary3=overall_summary3, total_time=total_time,
                           **orig_text)


@app.route('/')
def multi_article():
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
