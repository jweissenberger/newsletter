from transformers import T5ForConditionalGeneration, PegasusForConditionalGeneration, PegasusTokenizer
import nltk

if __name__ == '__main__':
    #nltk
    # nltk.download('vader_lexicon')
    # nltk.download('subjectivity')
    # nltk.download('punkt')
    # nltk.download('stopwords')

    # T5 model download
    model = T5ForConditionalGeneration.from_pretrained('t5-large')

    # pegasus download
    models = ['google/pegasus-xsum', 'google/pegasus-multi_news']
    for model in models:
        tokenizer = PegasusTokenizer.from_pretrained(model)
        pegasus = PegasusForConditionalGeneration.from_pretrained(model)
