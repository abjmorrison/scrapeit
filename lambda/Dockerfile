FROM abjmorrison/amoneys-repo:webscraper1.0

ADD pipelines pipelines

COPY lambda.py ./
CMD [ "lambda.handler" ]