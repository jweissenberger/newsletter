from nltk.tokenize import sent_tokenize

#TODO needs to change how we do quotes
def sentence_tokenizer(text):
    """
    Sentence tokenizer
    :param text:
    :return: list of sentences
    """
    text = text.replace('*', '')
    text = text.replace('-', '')
    text = text.replace('#', '')
    sentences = sent_tokenize(text)

    output = []
    for sentence in sentences:
        # remove super short sentences (usually titles or numbers or something)
        if len(sentence) < 8:
            continue
        else:
            output.append(sentence)

    return output


def plagiarism_checker(new_text, orig_text):

    new_text = new_text.lower()
    orig_text = orig_text.lower()

    orig_pladgerism = {}  # key is the number of the word in orig text and value is binary for if pladgerized
    for i in range(orig_text.split(' ')):
        orig_pladgerism[i] = False

    splits = new_text.split(' ')

    len_chunk = 7
    for i in range(len(splits) - len_chunk):
        chunk = splits[i:i+len_chunk]

        chunk_text = ''
        for j in chunk:
            chunk_text += j + ' '

        chunk_text = chunk_text.strip()

        if chunk_text in orig_text:
            print(chunk_text)


if __name__ == '__main__':

    a = "This is a test text, I want to see if this works, it should because I am just going to copy and paste part fo it"
    b = 'I want to see if this works, it should because I am'

    plagiarism_checker(new_text=b, orig_text=a)


