import MySQLdb, re
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
        self.db = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, db=self.database)
        self.cursor = self.db.cursor()

    def terminate(self):
        if self.cursor:
            self.cursor.close()

    def perform(self, sql):
        self.connect()

        if sql[-1] is not ';':
            sql = "{0};".format(sql)

        self.cursor.execute(sql)
        result = self.cursor.fetchall()

        self.terminate()
        if result:
            return result
        else:
            return None

class CorporaQuery:
    # CorporaQuery
    # Abstracts a search query. Used to generate a SQL statement from a complex set of customizable
    # user-defined parameters.

    def __init__(self, args):
        if args['min_relevancy'] is None:
            self.min_relevance = 1
        else:
            self.min_relevance = args['min_relevancy']

        self.cat_kp_list = parse_categories(args['category'])
        self.first_date = args['time_start']
        self.last_date = args['time_end']
        self.article_limit = args['article_limit']
        self.search_string = args['search_string'].replace("_"," ")

        self.set_flags()
        self.format_dates()
        self.sql = self.construct_sql()

    def get_result(self):
        # get_result()
        # Queries and returns formatted result associated with this query
        corpora = DatabaseConnection()

        result = corpora.perform(self.sql)

        # Catch empty results
        if result:
            cleaned_result = clean_search_results(result)
            return cleaned_result
        else:
            return None

    def set_flags(self):
        # set_flags()
        # Analyzes input data and sets a number of flags that instruct further methods how
        # to frame their SQL statements

        if self.search_string and len(self.search_string) is not 0:
            self.use_keywords = True
        else:
            self.use_keywords = False

        if self.article_limit is None:
            self.article_limit = "0" # Pass 0 as flag -> signal no limit

        self.format_dates()

    def format_dates(self):
        #format_dates()
        # Extension of set_flags used to set date flags and format them for
        # use in final SQL statement

        if self.first_date:
            self.sort_by_first = True

            self.first_date.replace('-', '')
            self.first_date = datetime(year=int(self.first_date[0:4]), month=int(self.first_date[4:6]), day=int(self.first_date[6:8]))
        else:
            self.sort_by_first = False

        if (self.last_date):
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
        esc_search_string = re.escape(self.search_string)
        title_SQL = []
        content_SQL = []

        # Full search string appearance
        title_SQL.append("if (title LIKE '%{0}%',10,0)".format(esc_search_string)) # 10 pts - title
        content_SQL.append("if (content LIKE '%{0}%',7,0)".format(esc_search_string))  # 7 pts - content

        # Keyword appearance
        for key in keyword_list:
            escaped_key = re.escape(key)
            title_SQL.append("if (title LIKE '%{0}%',5,0)".format(escaped_key))  # 5 pts - title
            content_SQL.append("if (content LIKE '%{0}%',3,0)".format(escaped_key))  # 3 - content

        return {'title_SQL':title_SQL, 'content_SQL':content_SQL}

    def construct_sql(self):
        # construct_sql()
        # Uses flags and substatements generated thus far to construct a massive SQL statement
        # that polls Corpora for all articles meeting the specified criteria
        sql = "SELECT *"

        if self.use_keywords:
            relevance_dict = self.build_keyword_relevance()
            title_SQL = relevance_dict['title_SQL']
            content_SQL = relevance_dict['content_SQL']

            title_string = ' + '.join(title_SQL)
            con_string = ' + '.join(content_SQL)

            if self.cat_kp_list:
                cat_string = ','.join([str(k) for k in cat_kp_list])


        if self.use_keywords:
            sql = "{0}, ({1} + {2}) AS relevance FROM articles a".format(sql, title_string, con_string)
            # If category specified -> look only in that category
            if self.cat_kp_list:
                sql = "{0} WHERE kp IN ({1})".format(sql, cat_string)
            sql = "{0} HAVING relevance > '{1}'".format(sql, self.min_relevance)
            # If also sorting by date -> prep statement to elaborate later
            if self.sort_by_first or self.sort_by_last:
                sql = "{0} AND ".format(sql)
        # If not using keywords -> begin SQL query with date
        elif self.sort_by_first or self.sort_by_last:
            sql = "{0} FROM articles a".format(sql)
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
        if self.use_keywords:
            sql = "{0} ORDER BY relevance DESC".format(sql)
        # If not doing any filtering whatsoever -> pull all the articles
        if not self.sort_by_first and not self.sort_by_last and not self.use_keywords:
            sql = "{0} FROM articles a".format(sql)
        # If enforcing limit -> do so ; Note '0' flag passed in url == no limit
        if int(self.article_limit) > 0:
            sql = "{0} LIMIT {1}".format(sql, self.article_limit)

        return sql

def parse_categories(category_string):
    # parse_categories():
    # Matches a string to a category (rss feeds), then pulls all matching article_source entries
    # to build and return a list of KPs for each article in this category

    corpora = DatabaseConnection()

    if category_string:
        # Match string to a list of RSS feeds
        sql = "SELECT feed FROM rss WHERE category = '{0}'".format(category_string)
        feed_list = corpora.perform(sql)
        feed_list = [feed for feed in feed_list[0]]
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
    # TODO: Import list from a maintained CSV?
    stop_word_list = ["in", "it", "a", "the", "of", "or", "I", "you", "he",
     "me", "us", "they", "she", "to", "but", "that", "this", "those", "then",
     "table", "drop", "delete"]
    c = 0
    # Collect non-stopwords and return
    for key in query:
        if key.lower() not in stop_word_list:
            words.append(key)
    return words

def clean_search_results(dirty_results):
    # clean_search_results():
    # Accepts raw tuple result from corpora_search, builds and returns
    # a list of dicts describing each extracted article
    clean_list = []

    for dirty in dirty_results:
        clean_results = {}

        clean_results['kp'] = dirty[0]
        clean_results['url'] = dirty[3]
        clean_results['title'] = dirty[4]
        clean_results['content'] = dirty[5]
        clean_results['summary'] = dirty[6]
        clean_results['keyword'] = dirty[7]
        clean_results['lang_claimed'] = dirty[8]
        clean_results['lang_detected'] = dirty[9]
        clean_results['confidence'] = dirty[10]
        clean_results['pub_date'] = dirty[11]
        clean_results['ret_date'] = dirty[12]
        clean_results['processed'] = dirty[13]
        clean_results['marked_by_proc'] = dirty[14]
        clean_results['bag_of_words'] = dirty[15]
        try:
            # If the user didn't use keywords, there will be no relevance in search clean_results
            clean_results['relevance'] = dirty[16]
        except IndexError:
            # Substitute 0 as a flag
            clean_results['relevance'] = 0

        clean_list.append(clean_results)
    return clean_list

def metric_primer(tables, toggle_counts=True, toggle_category=True):
    # metric_primer():
    # Semi-robust method to poll DB for metrics
    # Not as useful as originally intended - probably not necessary anymore
    result_dict = {}
    corpora = DatabaseConnection()

    # Pull counts of each request metric
    if toggle_counts:
        sql = ' UNION ALL '.join('SELECT count(*) FROM {0}'.format(table) for table in tables)
        count = corpora.perform(sql)
        result_dict['count'] = [c[0] for  c in count]

    # Grab categories and the count of feeds in each
    if toggle_category:
        sql = "SELECT category, COUNT(*) AS 'amount' FROM rss GROUP BY category;"

        result = corpora.perform(sql)
        categories = [c[0] for c in result]
        occurences = [c[1] for c in result]

        result_dict['rss'] = zip(categories, occurences)
        print result_dict['rss']

    return result_dict
