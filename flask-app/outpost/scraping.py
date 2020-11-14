import newspaper
from newspaper import Article
import pandas as pd


def pull_articles_from_source(url, source, article_data=[]):
    paper = newspaper.build(url)
    i = 0
    failed = 0
    print(len(paper.articles))
    paper.download_articles()
    paper.parse_articles()  # remove articles that are too small (probably not articles)
    print(len(paper.articles))
    for article in paper.articles:
        i += 1
        if i > 10:
            break
        try:
            # fail if the article is empty or less than 40 words
            if article.text.isspace() or article.text == '' or len(article.text.split(' ')) < 40:
                failed += 1
                continue
            article.nlp()

            authors = article.authors
            temp = []
            for i in authors:
                if len(i.split(' ')) > 5:
                    continue
                temp.append(i)
            authors = temp

            data = {'source': source, 'title': article.title, 'authors': authors, 'text': article.text,
                    'keywords': article.keywords, 'summary': article.summary, 'url': article.url,
                    'date': article.publish_date}
            article_data.append(data)
        except:
            failed += 1

    return article_data


def overall_scraper():
    sources = ['cnn', 'foxnews']

    article_data = []

    for i in sources:

        article_data = pull_articles_from_source(url=f'https://{i}.com', source=i, article_data=article_data)

    df = pd.DataFrame(article_data)

    df.to_csv('articles.csv', index=False)


def source_from_url(link):

    if 'www' in link:
        source = link.split('.')[1]
    else:
        if '.com' in link:
            source = link.split('.com')[0]
        else:
            source = link.split('.')[0]
    source = source.replace('https://', '')
    source = source.replace('http://', '')
    return source


def return_single_article(link, output_type='string'):
    """

    :param link:
    :param output_type: either 'string' or 'html'
    :return:
    """

    output = {}

    source = source_from_url(link=link)
    source_names = {'foxnews': 'Fox News',
                    'brietbart': 'Brietbart',
                    'wsj': 'Wall Street Journal',
                    'cnn': 'CNN',
                    'nytimes': 'New York Times',
                    'apnews': 'The Associated Press',
                    'msnbc': 'MSNBC',
                    'washingtonpost': 'The Washington Post'}
    source = source_names.get(source, source)

    article = Article(link)

    article.download()
    article.parse()

    authors = article.authors
    temp = []
    for i in authors:
        if len(i.split(' ')) > 5:
            continue
        temp.append(i)
    authors = temp

    by_line = ''
    if len(authors) == 1:
        by_line = f'By {authors[0]}'
    else:
        by_line = 'By '
        for i in authors:
            if i == authors[-1]:
                by_line += f'and {i}'
            else:
                by_line += f'{i}, '

    if output_type == 'html':
        new_line = '<br>'
    else:
        new_line = '\n'

    results = f'{source}:{new_line}{article.title}{new_line}{by_line}{new_line}{article.text}'

    article.nlp()
    summary = f'{source}:{new_line}{article.title}{new_line}{by_line}{new_line}{article.summary}'

    output['cleaned_article'] = results
    output['article'] = article.text
    output['summary'] = summary
    output['title'] = article.title
    output['authors'] = by_line
    output['source'] = source

    return output
