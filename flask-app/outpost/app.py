from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

from statistical_summarize import run_tf_idf_summarization, run_word_frequency_summarization
from subjectivity_analysis import textblob_topn_subjectivity
from sentiment_analysis import flair_topn_sentiment


# Initialize App
app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        rawtext = request.form['rawtext']

        # TODO check that num sentences is less than the total number of sentences

        tfidf_summary = run_tf_idf_summarization(rawtext, num_sentences=int(request.form['num_summary_sentences']))

        word_frequency_summary = run_word_frequency_summarization(rawtext, num_sentences=int(request.form['num_summary_sentences']))

        most_subjective, least_subjective = textblob_topn_subjectivity(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))

        top_positive, top_negative = flair_topn_sentiment(rawtext, num_sentences=int(request.form['num_subj_sent_sentences']))

    return render_template('analyze.html', tfidf_summary=tfidf_summary, word_frequency_summary=word_frequency_summary,
                           most_subjective=most_subjective, least_subjective=least_subjective,
                           top_positive=top_positive, top_negative=top_negative)


if __name__ == '__main__':
    app.run(debug=True)
