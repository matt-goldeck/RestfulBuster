# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from json import dumps
import datetime

from utils import DatabaseConnection, CorporaQuery
app = Flask(__name__)
api = Api(app)

class Multiple_Articles(Resource):
    def get(self):
        data_type = 'articles'
        article_list = get_corpora_results(data_type)

        response = {'count':len(article_list), 'articles':article_list}
        return response

class Free_Weibo(Resource):
    def get(self):
        data_type = 'freeweibo'
        post_list = get_corpora_results(data_type)

        response = {'count':len(post_list), 'posts':post_list}
        return response

class Novaya_Gazeta(Resource):
    def get(self):
        data_type = 'novaya_gazeta'
        article_list = get_corpora_results(data_type)

        response = {'count':len(article_list), 'articles':article_list}

        return response
class Specific_Article(Resource):
    def get(self):
        # one argument, no need to use Build_Get()
        parser = reqparse.RequestParser()
        parser.add_argument('kp', type=int, help='Unique identifier of stored article')
        args = parser.parse_args()

        query = CorporaQuery(args, plurality=False, data_type='articles')
        retrieved_article = query.get_result()

        # Process results; datetime not json-serializable, better solution exists (?)
        if retrieved_article:
            response = retrieved_article[0]
            response['pub_date'] = str(response['pub_date'])
            response['ret_date'] = str(response['ret_date'])
        else:
            response = none

        return response
class Corpora_Metrics(Resource):
    def get(self):
        # Very specific usage -> directly use DC() instead of CQ()
        corpora = DatabaseConnection()

        sql = "SELECT (SELECT COUNT(*) FROM articles) AS article_count, \
        (SELECT COUNT(*) FROM rss) AS rss_count, (SELECT COUNT(*) FROM \
        freeweibo) AS freeweibo_count, (SELECT COUNT(*) FROM freeweibo_topics) \
        AS freeweibo_topic_count, (SELECT COUNT(*) FROM novaya_gazeta) AS novaya_count FROM dual;"

        dirty_result = corpora.perform(sql)[0]
        clean_result = {}
        clean_result['article_count'] = dirty_result[0]
        clean_result['rss_count'] = dirty_result[1]
        clean_result['freeweibo_count'] = dirty_result[2]
        clean_result['freeweibo_topic_count'] = dirty_result[3]
        clean_result['novaya_count'] = dirty_result[4]

        response = clean_result

        return response

def get_corpora_results(data_type):
    # get_corpora_results()
    # Assembles a bespoke parser object, grabs arguments, and queries Corpora. Returns formatted
    # list.

    parser = build_get_parser(data_type=data_type)
    args = parser.parse_args()

    query = CorporaQuery(args, plurality = True, data_type=data_type)
    retrieved_items = query.get_result()

    # Process results; datetime not json-serializable TODO: better solution exists (?)
    item_list = []

    if retrieved_items:
        for item in retrieved_items:
            item['ret_date'] = str(item['ret_date']).encode("utf8")
            item['pub_date'] = str(item['pub_date']).encode("utf8")
            item_list.append(item)

    return item_list

def build_get_parser(data_type):
    # Builds a bespoke parser object for a given datatype and returns it

    parser = reqparse.RequestParser()
    parser.add_argument('min_relevancy', type=int, help='The minimum relevancy score to return an item.')
    parser.add_argument('time_start', help='The earliest point that an item could have been retrieved.')
    parser.add_argument('time_end', help='The latest point that an item could have been retrieved.')
    parser.add_argument('search_string', help='A string of words seperated by underscores.')
    parser.add_argument('item_limit', type=int, help='The maximum number of items to return.')
    parser.add_argument('offset', type=int, help='The offset of items to retrieve.')

    if data_type == 'articles':
        parser.add_argument('category', help='The category of RSS feed the article came from. Note: Only one')

    return parser

api.add_resource(Multiple_Articles, '/RestfulBuster/multi_article')
api.add_resource(Specific_Article, '/RestfulBuster/article')
api.add_resource(Corpora_Metrics, '/RestfulBuster/corpora_metrics')
api.add_resource(Free_Weibo, '/RestfulBuster/multi_weibo')
api.add_resource(Novaya_Gazeta, '/RestfulBuster/multi_novaya')

if __name__ == '__main__':
    app.run(debug=True)
