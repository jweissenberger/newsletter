from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

from statistical_summarize import run_tf_idf_summarization, run_word_frequency_summarization
from subjectivity_analysis import textblob_topn_subjectivity
from sentiment_analysis import flair_topn_sentiment
from hft5_summarizer import chunk_summarize_t5


# Initialize App
app = Flask(__name__)
Bootstrap(app)

# TODO make version number defined here maybe so that it can get updated on each of the templates


def clean_text(text):
    text = text.replace('*', '')
    text = text.replace('-', ' ')
    text = text.replace('#', '')

    return text


@app.route('/')
def summarize():
    return render_template('summarize.html')


@app.route('/summarize_result', methods=['GET', 'POST'])
def summarize_result():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        clean = clean_text(rawtext)

        large_summary = chunk_summarize_t5(clean, size='large')
        small_summary = chunk_summarize_t5(clean, size='small')

    return render_template('summarize_result.html', rawtext=rawtext, large_summary=large_summary,
                           small_summary=small_summary)


@app.route('/single')
def single():
    return render_template('single.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        rawtext = request.form['rawtext']

        # TODO check that num sentences is less than the total number of sentences

        rawtext = clean_text(rawtext)

        tfidf_summary = run_tf_idf_summarization(rawtext, num_sentences=int(request.form['num_summary_sentences']))

        word_frequency_summary = run_word_frequency_summarization(rawtext, num_sentences=int(request.form['num_summary_sentences']))

        most_subjective, least_subjective = textblob_topn_subjectivity(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))

        top_positive, top_negative = flair_topn_sentiment(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))

    return render_template('analyze.html', tfidf_summary=tfidf_summary, word_frequency_summary=word_frequency_summary,
                           most_subjective=most_subjective, least_subjective=least_subjective,
                           top_positive=top_positive, top_negative=top_negative)


@app.route('/multi_analyze', methods=['GET', 'POST'])
def multi_analyze():
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


        num_summary_sentences = int(request.form['num_summary_sentences'])
        num_subj_sent_sentences = int(request.form['num_subj_sent_sentences'])

        # TODO low priority: load flair model once so you don't need to do it on each call

        left_positive = []
        left_negative = []

        right_positive = []
        right_negative = []

        individual_article_results = {}
        for i in range(5):

            if cleaned_text[f'l_text{i+1}']:
                individual_article_results[f'tfidf_summary_l{i+1}'] = run_tf_idf_summarization(cleaned_text[f'l_text{i+1}'], num_sentences=num_summary_sentences)
                individual_article_results[f'word_frequency_summary_l{i+1}'] = run_word_frequency_summarization(cleaned_text[f'l_text{i + 1}'], num_sentences=num_summary_sentences)

                most_subjective, least_subjective = textblob_topn_subjectivity(cleaned_text[f'l_text{i+1}'], num_sentences=num_subj_sent_sentences)
                individual_article_results[f'most_subjective_l{i+1}'] = most_subjective
                individual_article_results[f'least_subjective_l{i + 1}'] = least_subjective

                top_positive, top_negative = flair_topn_sentiment(cleaned_text[f'l_text{i+1}'], num_sentences=num_subj_sent_sentences)
                individual_article_results[f'top_positive_l{i+1}'] = top_positive
                individual_article_results[f'top_negative_l{i + 1}'] = top_negative
                left_positive.extend(top_positive)
                left_negative.extend(top_negative)

            if cleaned_text[f'r_text{i+1}']:
                individual_article_results[f'tfidf_summary_r{i+1}'] = run_tf_idf_summarization(cleaned_text[f'r_text{i+1}'], num_sentences=num_summary_sentences)
                individual_article_results[f'word_frequency_summary_r{i+1}'] = run_word_frequency_summarization(cleaned_text[f'r_text{i + 1}'], num_sentences=num_summary_sentences)

                most_subjective, least_subjective = textblob_topn_subjectivity(cleaned_text[f'r_text{i+1}'], num_sentences=num_subj_sent_sentences)
                individual_article_results[f'most_subjective_r{i+1}'] = most_subjective
                individual_article_results[f'least_subjective_r{i + 1}'] = least_subjective

                top_positive, top_negative = flair_topn_sentiment(cleaned_text[f'r_text{i+1}'], num_sentences=num_subj_sent_sentences)
                individual_article_results[f'top_positive_r{i+1}'] = top_positive
                individual_article_results[f'top_negative_r{i + 1}'] = top_negative
                right_positive.extend(top_positive)
                right_negative.extend(top_negative)

        left_positive = sorted(left_positive, key=lambda x: x[0])
        left_positive = left_positive[-num_subj_sent_sentences:]

        right_positive = sorted(right_positive, key=lambda x: x[0])
        right_positive = right_positive[-num_subj_sent_sentences:]

        left_negative = sorted(left_negative, key=lambda x: x[0])
        left_negative = left_negative[-num_subj_sent_sentences:]

        right_negative = sorted(right_negative, key=lambda x: x[0])
        right_negative = right_negative[-num_subj_sent_sentences:]

    return render_template('multi_analyze.html', left_positive=left_positive, left_negative=left_negative,
                           right_positive=right_positive, right_negative=right_negative,
                           num_summary_sentences=num_summary_sentences,
                           num_subj_sent_sentences=num_subj_sent_sentences,
                           **orig_text, **individual_article_results)


@app.route('/multi_article')
def multi_article():
    return render_template('multi_article.html')


if __name__ == '__main__':
    app.run(debug=True)
