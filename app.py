from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from json import dumps
import datetime

from utils import DatabaseConnection, CorporaQuery
app = Flask(__name__)
api = Api(app)

class Multiple_Articles(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('min_relevancy', type=int, help='The minimum relevancy score to return an article.')
        parser.add_argument('time_start', help='The earliest point that an article could have been retrieved.')
        parser.add_argument('time_end', help='The latest point that an article could have been retrieved.')
        parser.add_argument('search_string', help='A string of words seperated by underscores.')
        parser.add_argument('article_limit', type=int, help='The maximum number of articles to return.')
        parser.add_argument('category', help='The category of RSS feed the article came from. Note: Only one')
        args = parser.parse_args()

        query = CorporaQuery(args, data_type="multiple_articles")
        retrieved_articles = query.get_result()

        article_list = []
        # Process results; datetime not json-serializable, better solution exists (?)
        if retrieved_articles:
            for article in retrieved_articles:
                article['pub_date'] = str(article['pub_date'])
                article['ret_date'] = str(article['ret_date'])
                article_list.append(article)

        response = {'count':len(article_list), 'articles':article_list}
        return response

class Specific_Article(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('kp', type=int, help='Unique identifier of stored article')
        args = parser.parse_args()

        query = CorporaQuery(args, data_type='specific_article')
        retrieved_article = query.get_result()

        # Process results; datetime not json-serializable, better solution exists (?)
        if retrieved_article:
            response = retrieved_article
            response[0]['pub_date'] = str(response[0]['pub_date'])
            response[0]['ret_date'] = str(response[0]['ret_date'])
        else:
            response = none

        return response
class Corpora_Metrics(Resource):
    def get(self):
        corpora = DatabaseConnection()

        sql = "SELECT (SELECT COUNT(*) FROM articles) AS article_count, \
        (SELECT COUNT(*) FROM rss) AS rss_count, (SELECT COUNT(*) FROM \
        freeweibo) AS freeweibo_count, (SELECT COUNT(*) FROM freeweibo_topics) \
        AS freeweibo_topic_count FROM dual;"

        dirty_result = corpora.perform(sql)[0]
        clean_result = {}
        clean_result['article_count'] = dirty_result[0]
        clean_result['rss_count'] = dirty_result[1]
        clean_result['freeweibo_count'] = dirty_result[2]
        clean_result['freeweibo_topic_count'] = dirty_result[3]

        response = clean_result

        return response

api.add_resource(Multiple_Articles, '/RestfulBuster/multi_article')
api.add_resource(Specific_Article, '/RestfulBuster/spec_article')
api.add_resource(Corpora_Metrics, '/RestfulBuster/corpora_metrics')


if __name__ == '__main__':
    app.run(debug=True)
