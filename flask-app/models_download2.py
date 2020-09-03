from transformers import PegasusForConditionalGeneration, PegasusTokenizer

if __name__ == '__main__':
    # pegasus download
    models = ['google/pegasus-cnn_dailymail',
              'google/pegasus-multi_news', 'google/pegasus-gigaword']
    for model in models:
        tokenizer = PegasusTokenizer.from_pretrained(model)
        pegasus = PegasusForConditionalGeneration.from_pretrained(model)