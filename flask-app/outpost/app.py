from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

from statistical_summarize import run_tf_idf_summarization, run_word_frequency_summarization
from subjectivity_analysis import textblob_topn_subjectivity
from sentiment_analysis import flair_topn_sentiment


# Initialize App
app = Flask(__name__)
Bootstrap(app)

# TODO make version number defined here maybe so that it can get updated on each of the templates

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        rawtext = request.form['rawtext']

        # TODO check that num sentences is less than the total number of sentences
        # TODO remove special characters from the text

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






    return render_template('multi_analyze.html', **orig_text)



@app.route('/multi_article')
def multi_article():
    return render_template('multi_article.html')


if __name__ == '__main__':
    app.run(debug=True)
