from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import time

from hf_summarizer import chunk_summarize_t5, pegasus_summarization
from common import sentence_tokenizer, plagiarism_checker, clean_text
from scraping import return_single_article
from statistical_summarize import run_tf_idf_summarization

# Initialize App
app = Flask(__name__)
Bootstrap(app)

VERSION = 'v0.1.0'


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

        results, summary, _ = return_single_article(link, output_type='html')

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

        # TODO: title generation with xsum -> is it worth it right now? Would add an extra minute ish to this

        orig_text = {}
        left_text = ''
        right_text = ''
        left_summaries = ''
        right_summaries = ''

        # get right and left articles, summaries
        for s in ['l', 'r']:
            for i in range(5):

                orig_text[f'{s}_link{i+1}'] = request.form[f'{s}_link{i+1}']
                # if a link is given use newsarticle3k else parse the given text
                if orig_text[f'{s}_link{i+1}']:
                    article, summary, title = return_single_article(orig_text[f'{s}_link{i+1}'], output_type='string')
                    if s == 'l':
                        left_summaries += summary + '||||'
                        left_text += article + '||||'
                    else:
                        right_summaries += summary + '||||'
                        right_text += article + '||||'

                elif request.form[f'{s}_text{i+1}']:
                    orig_text[f'{s}_text{i + 1}'] = request.form[f'{s}_text{i+1}']

                    clean = clean_text(orig_text[f'{s}_text{i + 1}'])
                    if s == 'l':
                        left_text += clean + '||||'
                        left_summaries += run_tf_idf_summarization(clean, 6) + '||||'
                    else:
                        right_text += clean + '||||'
                        right_summaries += run_tf_idf_summarization(clean, 6) + '||||'

        # generate left and right summaries
        # pass the summaries into multi news
        left_summary1 = pegasus_summarization(text=left_summaries, model_name='google/pegasus-multi_news')
        left_summary1 = plagiarism_checker(new_text=left_summary1, orig_text=left_text)

        right_summary1 = pegasus_summarization(text=right_summaries, model_name='google/pegasus-multi_news')
        right_summary1 = plagiarism_checker(new_text=right_summary1, orig_text=right_text)

        # pass each article individually into multi news
        print(left_text.split('||||'))
        left_summary3 = ''
        for i in left_text.split('||||')[:-1]:
            left_summary3 += pegasus_summarization(text=i, model_name='google/pegasus-multi_news') + '<br>'
        left_summary3 = plagiarism_checker(new_text=left_summary3, orig_text=left_text)

        right_summary3 = ''
        for i in right_text.split('||||')[:-1]:
            right_summary3 += pegasus_summarization(text=i, model_name='google/pegasus-multi_news') + '<br>'
        right_summary3 = plagiarism_checker(new_text=right_summary3, orig_text=right_text)

        # generate overall summaries
        overall_summary1 = chunk_summarize_t5(left_summary1 + ' ' + right_summary1, size='large')
        overall_summary1 = plagiarism_checker(new_text=overall_summary1, orig_text=right_text + ' ' + left_text)

        overall_summary3 = chunk_summarize_t5(left_summary3 + ' ' + right_summary3, size='large')
        overall_summary3 = plagiarism_checker(new_text=overall_summary3, orig_text=right_text + ' ' + left_text)

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
