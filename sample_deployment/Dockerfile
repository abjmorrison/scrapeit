FROM abjmorrison/amoneys-publicrepo:scrapeit1.1

ADD pipelines pipelines

COPY lambda/htmlScrapeit_lambda.py ./
CMD [ "htmlScrapeit_lambda.handler" ]