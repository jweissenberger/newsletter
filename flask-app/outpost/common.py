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

    splits = new_text.split(' ')

    new_pladgerism = {}  # key is the number of the word in orig text and value is binary for if pladgerized
    for i in range(len(splits)):
        new_pladgerism[i] = False

    len_chunk = 4
    for i in range(len(splits) - len_chunk):
        chunk = splits[i:i+len_chunk]

        chunk_text = ''
        for j in chunk:
            chunk_text += j + ' '

        chunk_text = chunk_text.strip()

        if chunk_text in orig_text:
            for j in range(i, i+len_chunk+1):
                new_pladgerism[j] = True

    # print out
    open = '<span style="color:red;">'
    close = '</span>'
    output = ''
    for i in range(len(splits)):
        # first element is stolen
        if i == 0 and new_pladgerism[0]:
            output += open + splits[i] + ' '
            continue

        # non first element is stolen (first of bunch)
        if new_pladgerism[i] and not new_pladgerism[i - 1]:
            output += open + splits[i] + ' '
            continue

        # last element is stolen
        if new_pladgerism[i] and i == len(splits) - 1:
            output += splits[i] + close
            continue

        # middle of a bunch of stolen elements
        if new_pladgerism[i] and new_pladgerism[i+1] and new_pladgerism [i - 1]:
            output += splits[i] + ' '

        # end of a bunch of stolen
        if new_pladgerism[i] and not new_pladgerism[i + 1]:
            output += splits[i] + close + ' '
            continue

        # element not stolen
        if not new_pladgerism[i]:
            output += splits[i] + ' '

    return output


if __name__ == '__main__':

    a = "This is a test text, I want to see if this works, it should because I am just going to copy and paste part fo it"
    b = 'neither is this. I want to see if this works, it should because I am. but this part is not stolen This is a test text, I want'

    print(plagiarism_checker(new_text=b, orig_text=a))


