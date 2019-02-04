# -*- coding: utf-8 -*-
import MySQLdb, re
from datetime import datetime
from secrets import corpora # Bad! Fix this later.
class DatabaseConnection:
    # DatabaseConnection represents a connection to the database (defaults to Corpora)
    # and contains a few useful functions to abstract functionality from main classes

    database = cursor = host = username = password = db = None

    def __init__(self, credentials = corpora):
        # Default to corpora
        if credentials:
            self.database = credentials['database']
            self.password = credentials['password']
            self.host = credentials['host']
            self.username = credentials['username']
    def connect(self):
        self.db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password,
         db=self.database, use_unicode=True)
        self.cursor = self.db.cursor()

    def terminate(self):
        if self.cursor:
            self.db.commit()

            self.cursor.close()
            self.db.close()

    def perform(self, sql):
        self.connect()

        if sql[-1] is not ';':
            sql = "{0};".format(sql)

        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        self.terminate()

        return result

class CorporaQuery:
    # CorporaQuery
    # Abstracts a search query. Used to generate a SQL statement from a complex set of customizable
    # user-defined parameters.

    def __init__(self, args, plurality, data_type):
        self.plurality = plurality # Determines retrieval or search
        self.data_type = data_type # Determines what we're looking for

        self.process_parameters(args)
        self.sql = self.construct_sql()
        self.scrubbed_results = None

    def process_parameters(self, args):
        # process_parameters()
        # Robust class function that determines which item to search for and how to search for it

        # Multiple items a.k.a. hybrid search functionality
        if self.plurality:
            if args['min_relevancy']:
                self.min_relevance = args['min_relevancy']
            else:
                self.min_relevance = 1

            self.first_date = args['time_start']
            self.last_date = args['time_end']
            self.item_limit = args['item_limit']

            # Perform tests on the data to determine which functionality to perform
            self.set_flags(args)

            # Format dates for use in SQL
            self.format_dates()

        # Retrieving single item a.k.a. specific retrieval
        else:
            self.kp = args['kp']
    def get_result(self, repeat_search=False):
        # get_result()
        # Queries and returns formatted result associated with this query

        corpora = DatabaseConnection()
        print self.sql

        # If we haven't generated a result or we're repeating the search, query the DB
        if not self.scrubbed_results or repeat_search:
            dirty_result = corpora.perform(self.sql)
            if dirty_result:
                self.scrub_results(dirty_result)
            else:
                self.scrubbed_results = None

        return self.scrubbed_results

    def set_flags(self, args):
        # set_flags()
        # Analyzes input data and sets a number of flags that inform further methods how
        # to frame their SQL statements

        # Was a search string specified and is it legal? If so, format it and store it.
        if args['search_string'] and len(args['search_string']) is not 0:
                self.search_string = args['search_string'].replace("_"," ")
        else:
            self.search_string = None

        if self.item_limit is None:
            self.item_limit = "500" # Default max item limit to 500

        # Specific data_type functionality
        if self.data_type == 'articles' and args['category']:
            self.category = args['category']
            self.cat_kp_list = parse_categories(self.category)
        else:
            self.category = None
            self.cat_kp_list = None

    def format_dates(self):
        # format_dates()
        # Extension of set_flags used to set date flags and format them for
        # use in final SQL statement

        if self.first_date:
            self.sort_by_first = True

            self.first_date.replace('-', '')
            self.first_date = datetime(year=int(self.first_date[0:4]), month=int(self.first_date[4:6]), day=int(self.first_date[6:8]))
        else:
            self.sort_by_first = False

        if self.last_date:
            self.sort_by_last = True

            self.last_date.replace('-', '')
            self.last_date = datetime(year=int(self.last_date[0:4]), month=int(self.last_date[4:6]), day=int(self.last_date[6:8]))
        else:
            self.sort_by_last = False

    def build_keyword_relevance(self):
        # build_keyword_relevance()
        # Parses keywords and constructs substatements that search for them, and add to
        # an article's 'relevance score' if found

        keyword_list = filter_search_keys(self.search_string)
        esc_search_string = re.escape(self.search_string).encode("utf8")

        # If data type has a title -> look in it
        title_SQL = []
        if self.data_type == 'articles':
            # Full search string appearance
            title_SQL.append("if (title LIKE '%{0}%',10,0)".format(esc_search_string)) # 10 pts - title

        content_SQL = []
        # Full search string appearance
        content_SQL.append("if (content LIKE '%{0}%',7,0)".format(esc_search_string))  # 7 pts - content

        # Keyword appearance
        for key in keyword_list:
            escaped_key = re.escape(key)
            if self.data_type == 'articles':
                title_SQL.append("if (title LIKE '%{0}%',5,0)".format(escaped_key))  # 5 pts - title
            content_SQL.append("if (content LIKE '%{0}%',3,0)".format(escaped_key))  # 3 - content

        return {'title_SQL':title_SQL, 'content_SQL':content_SQL}

    def construct_sql(self):
        # construct_sql()
        # Uses flags and substatements generated thus far to construct a big SQL statement
        # that polls Corpora for all items meeting the specified criteria
        sql = "SELECT *"

        # If not plural, skip over complex sql construction
        if not self.plurality:
            sql = "SELECT * FROM {0} WHERE kp = '{1}'".format(self.data_type, self.kp)
            return sql

        # If using search functinality -> process keywords
        if self.search_string:
            relevance_dict = self.build_keyword_relevance()
            title_SQL = relevance_dict['title_SQL']
            content_SQL = relevance_dict['content_SQL']

            title_string = ' + '.join(title_SQL)
            con_string = ' + '.join(content_SQL)

            if self.cat_kp_list:
                cat_string = ','.join([str(k) for k in self.cat_kp_list])

        # Long branching decision tree to build keyword search dependent on multiple variables
        if self.search_string:
            sql = "{0}, ({1} + {2}) AS relevance FROM {3} a".format(sql, title_string, con_string,
            self.data_type)
            # If category specified -> look only in that category
            if self.cat_kp_list:
                sql = "{0} WHERE kp IN ({1})".format(sql, cat_string)
            sql = "{0} HAVING relevance > '{1}'".format(sql, self.min_relevance)
            # If also sorting by date -> prep statement to elaborate later
            if self.sort_by_first or self.sort_by_last:
                sql = "{0} AND ".format(sql)
        # If not using keywords -> begin SQL query with date
        elif self.sort_by_first or self.sort_by_last:
            sql = "{0} FROM {1} a".format(sql, self.data_type)
            # If category specified -> look only in that category
            if self.cat_kp_list:
                sql = "{0} WHERE kp IN ({1})".format(sql, cat_string)
            sql = "{0} HAVING".format(sql)
        # If using date/time -> query for dates
        if self.sort_by_first:
            sql = "{0} pub_date > '{1}'".format(sql, self.first_date)
            # If also sorting by last -> accommodate sorting by last
            if self.sort_by_last:
                sql = "{0} AND".format(sql)
        # If sorting by last -> query for last
        if self.sort_by_last:
            sql = "{0} pub_date < '{1}'".format(sql, self.last_date)
        # If using keywords, order by relevance in descending order
        if self.search_string:
            sql = "{0} ORDER BY relevance DESC".format(sql)
        # If not doing any filtering whatsoever -> pull all the articles
        if not self.sort_by_first and not self.sort_by_last and not self.search_string:
            sql = "{0} FROM {1} a".format(sql, self.data_type)
        # If enforcing limit -> do so;
        if self.item_limit and int(self.item_limit) > 0:
            sql = "{0} LIMIT {1}".format(sql, self.item_limit)

        return sql

    def scrub_results(self, dirty_results):
        # scrub_results()
        # Properly format and 'clean' raw data from SQL for final json object

        clean_list = []

        # Did we use search? Set a flag so later methods know to look for a rel score.
        if self.plurality:
            if self.searh_string:
                relevance = True
        else:
            relevance = False

        for dirty in dirty_results:
            if self.data_type == 'articles':
                clean_result = build_article_dictionary(dirty, relevance)
            elif self.data_type == 'novaya_gazeta':
                clean_result = build_novaya_dictionary(dirty, relevance)
            elif self.data_type == 'freeweibo':
                clean_result = build_freeweibo_dictionary(dirty, relevance)

            print "Cleaned", "Pub_date", clean_result['pub_date'], 'Ret_date', clean_result['ret_date']
            clean_list.append(clean_result)

        self.scrubbed_results = clean_list


def parse_categories(category_string):
    # parse_categories():
    # Matches a string to a category (rss feeds), then pulls all matching article_source entries
    # to build and return a list of KPs for each article in this category

    corpora = DatabaseConnection()
    if category_string:
        # Match string to a list of RSS feeds
        sql = "SELECT feed FROM rss WHERE category = '{0}'".format(category_string)
        feed_list = corpora.perform(sql)
        feed_list = ["'{0}'".format(feed) for feed in feed_list[0]]
        # Create list of all article KP's in the specified category
        sql = "SELECT article_id FROM article_source WHERE source IN ({0})".format(','.join(feed_list))

        raw_cat_kp_list = corpora.perform(sql)
        cat_kp_list = []

        for kp in raw_cat_kp_list:
            cat_kp_list.append(kp[0])
    else:
        cat_kp_list = None

    return cat_kp_list

def filter_search_keys(query):
    # filter_search_keys():
    # Parses query into a list of strings. Filters out stopwords.
    # Returns list of strings.
    query = query.split()
    words = []
    # TODO: Import list from a maintained CSV? Non-linear search with sorted stop_word_list?
    stop_word_list = ["in", "it", "a", "the", "of", "or", "I", "you", "he",
     "me", "us", "they", "she", "to", "but", "that", "this", "those", "then",
     "table", "drop", "delete"]
    c = 0
    # Collect non-stopwords, encode to utf8, and return
    for key in query:
        if key.lower() not in stop_word_list:
            words.append(key.encode("utf8"))
    return words

def build_article_dictionary(dirty_result, relevance):
    # build_article_dictionary()
    # Builds dictionary representing an RSS article from a dirty SQL result
    clean_result = {}

    clean_result['kp'] = dirty_result[0]
    clean_result['url'] = dirty_result[3]
    clean_result['title'] = dirty_result[4]
    clean_result['content'] = dirty_result[5]
    clean_result['summary'] = dirty_result[6]
    clean_result['keyword'] = dirty_result[7]
    clean_result['lang_claimed'] = dirty_result[8]
    clean_result['lang_detected'] = dirty_result[9]
    clean_result['confidence'] = dirty_result[10]
    clean_result['pub_date'] = dirty_result[11]
    clean_result['ret_date'] = dirty_result[12]
    clean_result['processed'] = dirty_result[13]
    clean_result['marked_by_proc'] = dirty_result[14]
    clean_result['bag_of_words'] = dirty_result[15]

    clean_result = try_relevance(dirty_result, clean_result, relevance)

    return clean_result

def build_novaya_dictionary(dirty_result, relevance):
    # build_novaya_dictionary()
    # Builds dictionary representing a Novaya article from a dirty SQL result
    clean_result = {}

    clean_result['kp'] = dirty_result[0]
    clean_result['pub_date'] = dirty_result[1].date()
    clean_result['author'] = dirty_result[2]
    clean_result['original_post'] = dirty_result[3]
    clean_result['content'] = dirty_result[4]
    clean_result['category'] = dirty_result[5]
    clean_result['ret_date'] = dirty_result[6].date()

    clean_result = try_relevance(dirty_result, clean_result, relevance)

    return clean_result

def build_freeweibo_dictionary(dirty_result, relevance):
    # build_freeweibo_dictionary()
    # Builds dictionary representing a freeweibo post from a dirty SQL result
    clean_result = {}

    clean_result['kp'] = dirty_result[0]
    clean_result['content'] = dirty_result[2]
    clean_result['weibo_id'] = dirty_result[4]
    clean_result['pub_date'] = dirty_result[5]
    clean_result['ret_date'] = dirty_result[6]
    clean_result['lang_detected'] = dirty_result[7]
    clean_result['confidence'] = dirty_result[8]
    clean_result['bag_of_words'] = dirty_result[11]

    clean_result = try_relevance(dirty_result, clean_result, relevance)

    return clean_result

def try_relevance(dirty_result, clean_result, relevance):
    # try_relevance()
    # Method to assign a relevance score
    if relevance:
        clean_result['relevance'] = dirty_result[-1]
    else:
        clean_result['relevance'] = 0

    return clean_result
