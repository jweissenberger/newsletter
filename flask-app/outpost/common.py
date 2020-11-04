from nltk.tokenize import sent_tokenize


def sentence_tokenizer(text):
    """
    Sentence tokenizer
    :param text: string of text to be separated by sentences
    :return: list of sentences
    """
    text = text.replace('*', '')
    text = text.replace('-', '')
    text = text.replace('#', '')

    # keep quotes together
    in_quote = False
    new_text = ''
    for char in text:
        if char == '"':
            in_quote = not in_quote

        if in_quote and char == '.':
            new_text += '<quote_period>'
        else:
            new_text += char
    text = new_text

    sentences = sent_tokenize(text)

    output = []
    for sentence in sentences:
        # remove super short sentences (usually titles or numbers or something)
        if len(sentence) < 8:
            continue
        else:
            output.append(sentence)

    for i in range(len(output)):
        output[i] = output[i].replace('<quote_period>', '.')

    return output


def plagiarism_checker(new_text, orig_text):

    # TODO, fix handling of quotes not being attributed

    new_text = new_text.lower()
    orig_text = orig_text.lower()

    splits = new_text.split(' ')

    new_plagiarism = {}  # key is the number of the word in orig text and value is binary for if pladgerized
    for i in range(len(splits)):
        new_plagiarism[i] = False

    len_chunk = 4
    for i in range(len(splits) - len_chunk):
        chunk = splits[i:i+len_chunk]

        chunk_text = ''
        for j in chunk:
            chunk_text += j + ' '

        chunk_text = chunk_text.strip()

        if chunk_text in orig_text:
            for j in range(i, i+len_chunk+1):
                new_plagiarism[j] = True

    # print out
    open = '<span style="color:red;">'
    close = '</span>'
    output = ''
    words_plagiarized = 0
    for i in range(len(splits)):
        if new_plagiarism[i]:
            words_plagiarized += 1

        # first element is stolen
        if i == 0 and new_plagiarism[0]:
            output += open + splits[i] + ' '
            continue

        # non first element is stolen (first of bunch)
        if new_plagiarism[i] and not new_plagiarism[i - 1]:
            output += open + splits[i] + ' '
            continue

        # last element is stolen
        if new_plagiarism[i] and i == len(splits) - 1:
            output += splits[i] + close
            continue

        # middle of a bunch of stolen elements
        if new_plagiarism[i] and new_plagiarism[i+1] and new_plagiarism[i - 1]:
            output += splits[i] + ' '

        # end of a bunch of stolen
        if new_plagiarism[i] and not new_plagiarism[i + 1]:
            output += splits[i] + close + ' '
            continue

        # element not stolen
        if not new_plagiarism[i]:
            output += splits[i] + ' '

    # calculate % plagiarism
    percent_plagiarism = (words_plagiarized / len(splits)) * 100
    output = f'Percent Plagiarism: {percent_plagiarism}%<br>' + output

    #TODO fix capitalization with sentence tokenizer

    return output


def clean_text(text):

    text = text.replace('&', 'and')

    allowed_symbols = ['"', "'", ' ', '$', ':', '.', '?', '!', '(', ')', '/', ';']

    new_text = ""
    for char in text:
        if char.isalnum() or char in allowed_symbols:
            new_text += char

    return new_text


if __name__ == '__main__':

    a = "This is a test text, I want to see if this works, it should because I am just going to copy and paste part fo it"
    b = 'neither is this. I want to see if this works, it should because I am. but this part is not stolen This is a test text, I want'

    print(plagiarism_checker(new_text=b, orig_text=a))


