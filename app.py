from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from json import dumps
import datetime

from utils import DatabaseConnection, CorporaQuery
app = Flask(__name__)
api = Api(app)

class Articles(Resource):
    def get(self):
        corpora = DatabaseConnection()

        parser = reqparse.RequestParser()
        parser.add_argument('min_relevancy', type=int, help='Rate to charge for this resource')
        parser.add_argument('time_start', type=datetime, help='Rate to charge for this resource')
        parser.add_argument('time_end', type=datetime, help='Rate to charge for this resource')
        parser.add_argument('search_string', help='Rate to charge for this resource')
        parser.add_argument('article_limit', type=int, help='Rate to charge for this resource')
        parser.add_argument('category', help='Rate to charge for this resource')
        args = parser.parse_args()

        query = CorporaQuery(args)
        retrieved_articles = query.get_result()
        article_list = []

        # Check for no results (empty)
        if retrieved_articles:
            for article in retrieved_articles:
                run_dict = {'Title':article['title'], 'KP':article['kp'], 'Relevance':article['relevance']}
                article_list.append(run_dict)

        response = {'count':len(article_list), 'articles':article_list}
        return response

api.add_resource(Articles, '/RestfulBuster/Articles')


if __name__ == '__main__':
    app.run(debug=True)
