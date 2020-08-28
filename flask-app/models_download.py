from transformers import T5Tokenizer, T5ForConditionalGeneration
import nltk

if __name__ == '__main__':
    #nltk
    nltk.download('vader_lexicon')
    nltk.download('subjectivity')
    nltk.download('punkt')
    nltk.download('stopwords')

    # T5 model download
    model = T5ForConditionalGeneration.from_pretrained('t5-large')
    model = T5ForConditionalGeneration.from_pretrained('t5-small')