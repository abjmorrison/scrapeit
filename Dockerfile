FROM abjmorrison/amoneys-repo:webscraper1.0

ADD pipelines pipelines

COPY lambda/htmlScrapeit_lambda.py ./
CMD [ "htmlScrapeit_lambda.handler" ]