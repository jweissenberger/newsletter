# Outpost API

Use Machine Learning to automatically generate news articles in an easy to use web app.

Stack: 
- Flask
- Docker
- Celery
- Gunicorn
- Nginx
- HuggingFace
- NewsPaper3k

## HuggingFace
The important ML models for this repo are taken from HuggingFace's transformers library.
The models that showed the best performance were Google Pegasus and DistilBart both trained on 
the CNN-Dailymail dataset. Many other Pegasus, T5 and other ML models were tested and are still 
available within the 

## NewsPaper3k
Used for websraping and pulling the articles from a link


## TODO's
- Finish scraping to pull from all of the sources
- Store the scraped results in the flask session so we don't have to pull them more than once (ideally should be stored in a database)
- Add a loading screen to scraping because each source it pulls from takes about 3 seconds
- Add a celery task queue for article generation so that users to have to be hanging on a waiting screen
- Use Bootstrap and CSS to make it cleaner


## Future improvements:
- Because the NLP models are so large its recommended that a large/GPU AWS EC2 Instance is used
so that article generation doesn't take too long. This would be expensive to leave running if you
only use it a couple times a day. Offloading the computation to an AWS Batch autoscaling group with 
a minimum size of 0 would be much more cost effective (Do scraping and kick of jobs from a small
EC2 and then use boto3 calls to the Batch cluster)
- NewsAPI to pull articles and find trending topics (super expensive though)
- Auto generate articles based off of trending topics (Get trending news articles and then pull 
similar articles based off of keywords)
- Use Flask-login to make user access more secure
- Store previously generated articles in a db
- release the summarization python code as a pip package
- Release the whole api to AWS Marketplace as a base image
- Accept both text and links as input


