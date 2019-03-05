# RestfulBuster: A simple RESTful API in Flask
Provides easy access and search through content on the NetSci Lab database. An evolution of my very crudely constructed CensorBuster interface in Django used prior.

Works in conjuction with Apollo -> https://github.com/leberkc/nlp-news-aggregator

More information can be found -> www.netsci.montclair.edu 

# Basic Gist
A collection of content useful in studies of government web censorship is either manually or automatically extracted and then stored on a MySQL server at Montclair State University. This application aims to provide easy, RESTful access to the aforementioned content. As of right now this content, broadly speaking, is:
 - RSS Articles: Articles scraped from RSS feeds in both their original text form and a processed 'bag-of-words'. Associated metrics are included.
 - FreeWeibo Content: Posts and topics that have been determined to have been censored by the FreeWeibo Project. Stored similarly to articles.
 - Novaya Gazeta: Articles from the Novaya Gazeta, a Russian newspaper known for critical and controversial coverage of political and social affairs in Russia.
 
Search through this content works very crudely. I ~~stole~~ was inspired by some common blog search algorithms that look through the content of each post and assign points based on whether or not the whole query or parts of the query are present. As news articles and social media posts are very similiar to blogs, I felt this suited the need rather well. Relevance points are assigned very unscientifically to the standard of "I had a good gut feeling about it." They are described in this table:

Match | Score
------|------
Complete phrase in the title | 10
Complete phrase in the content | 7
Keyword appearance in the title | 5
Keyword appearance in the content | 3

Search is generalized and abstracted in the CorporaQuery object as to provide search through any medium stored in Corpora with only minimal overhead. 

Note: Stored FreeWeibo posts and Novaya articles have no titles, and thus points are currently not assigned for appearances in them.
 

# Endpoints
There are currently **5** endpoints. Shorthand, they look like this:

Method | URL | Params | Results
-------|-----|--------|----------
GET|/api/corpora_metrics|None| Returns counts of entries in database
GET|/api/article|kp| Returns the information of a specific article
GET|/api/multi_article|category, search_string, time_start, time_end, item_limit| Returns array of article objects and a count
GET|/api/multi_novaya|search_string, time_start, time_end, item_limit| Returns array of article objects and a count
GET|/api/multi_weibo|search_string, time_start, time_end, item_limit| Returns array of weibo posts and a count


## Specific_Article
Provides access to a single article, specified by the KP parameter. Very straightforward. This functionality *should* be abstracted as to provide access to specific points in other data types.

**HTTP Request**

`GET api/article`

**Parameters:**
- kp: The unique primary key assigned to the article. 

**Example:**

Input: 

`http://www.___.com/api/article?kp=1`

Output: 
```
{
    "bag_of_words": "local, college, student, toast, morning, authorities, report, morning, matthew, goldeck, new, jersey, slices, toasted, bread, parents, kitchen, bread, incident, confirmed, sources, report, matthew, prefers, pumpernickel, throughout, day, updates",
    "confidence": 0.363515,
    "content": "MattNews: A local college student made toast this morning. Authorities report that sometime between the hours of 7 and 9 in the morning, Matthew Goldeck of New Jersey produced two slices of toasted bread in his parent's kitchen. While the exact variety of bread used in the incident has not been confirmed, sources close to the matter report Matthew prefers pumpernickel. Check back throughout the day for updates.",
    "keyword": "college, student, toast, pumpernickel"
    "kp": 1,
    "lang_claimed": "en",
    "lang_detected": "en",
    "marked_by_proc": 2737,
    "processed": 1,
    "pub_date": "2017-12-12 00:59:00",
    "relevance": 0,
    "ret_date": "2018-01-07 14:54:59",
    "summary": "A local college student made toast this morning",
    "title": "Local College Student Further Bakes Baked Goods",
    "url": "http://www.mattnews.com/breaking/garbage?source=connect.github"
}
```
## Multiple_Article
Provides search through the database of collected articles. If no parameters are specified, 500 articles will be returned.

**HTTP Request**

`GET api/multi_article`

**Parameters:**
- category: The category of RSS feed this article came from. Matched against the rss table then joined with the article_source table. Only one category can be specified. If no value is specified, defaults to all categories. 
- search_string: Text separated by underscores. Stop words and dangerous words are removed from a maintained list before usage in SQL. If no value is specified, does not use text-based search.
- min_relevancy: The minimum relevance score for an article to show up in search results. If no value is specified, defaults to 1.
- time_start: The earliest point an article could have been published to return in the search results. If no value is specified, pulls article from earliest point.
- time_end: The latest point an article could have been published to return in the search results. If no value is specified, pulls articles up until latest point.
- item_limit: The maximum number of articles to return in the search. If no value specified, defaults to 500.

**Example:**

Input:
`http://www.____.com/api/multi_article?search_string=toast_college_student&time_end=19960101&time_start=20180101&min_relevancy=3&item_limit=1&category=Domestic`
```
{
    "articles": [
        {
        "bag_of_words": "local, college, student, toast, morning, authorities, report, morning, matthew, goldeck, new, jersey, slices, toasted, bread, parents, kitchen, bread, incident, confirmed, sources, report, matthew, prefers, pumpernickel, throughout, day, updates",
        "confidence": 0.363515,
        "content": "MattNews: A local college student made toast this morning. Authorities report that sometime between the hours of 7 and 9 in the morning, Matthew Goldeck of New Jersey produced two slices of toasted bread in his parent's kitchen. While the exact variety of bread used in the incident has not been confirmed, sources close to the matter report Matthew prefers pumpernickel. Check back throughout the day for updates.",
        "keyword": "college, student, toast, pumpernickel"
        "kp": 1996,
        "lang_claimed": "en",
        "lang_detected": "en",
        "marked_by_proc": 2737,
        "processed": 1,
        "pub_date": "2017-12-12 00:59:00",
        "relevance": 8.0,
        "ret_date": "2018-01-07 14:54:59",
        "summary": "A local college student made toast this morning",
        "title": "Local College Student Further Bakes Baked Goods",
        "url": "http://www.mattnews.com/breaking/garbage?source=connect.github"
        },
        {
            "bag_of_words": "local, college, student, toast, university, arrested, charges, assault, battery, altercation, broke, botched, toast, schools, mascot, toasty, administration, toast, college, publically, student, timothy, tortilla, stringent, toasting, policy, statement, deans, office, toast, university, toasting, etiquette, condone, lackluster, table, manners, campus, police, charges, tortilla, official, televised, apology, toasty, students, faculty, TU",
            "confidence": 0.9678,
            "content": "MattNews: A local college student from Toast University was arrested today on charges of assault and battery after an altercation broke out when he botched a toast to the school's mascot, Toasty. The administration of Toast College has publically spoken out against the student, 21 year old Timothy Tortilla, citing their stringent toasting policy. A statement from the dean's office said that "(students) at Toast University are held to an extremely high level of toasting etiquette. We do not condone such lackluster table manners." Campus police say that the charges Mr. Tortilla faces are serious, but can be reduced with an official and televised apology to Toasty and the students and faculty of TU."
            "keyword": "college, student, toast university, toast, police, assault, arrest",
            "kp": 2,
            "lang_claimed": "en",
            "lang_detected": "en",
            "marked_by_proc": 250,
            "processed": 1,
            "pub_date": "2018-12-21 00:23:00",
            "relevance": 18.0,
            "ret_date": "2019-01-08 11:20:10",
            "summary": "A Toast University college student was arrest on assault and battery this Tuesday.",
            "title": "Toast College Student Arrested in Toasting Scandal",
            "url": "https://www.mattnews.com/breaking/garbage?source=connect.github"
        }
    ],
    "count": 2
}
```
## Novaya_Gazeta
Provides search through the database of collected articles. If no parameters are specified, 500 articles will be returned. Note that stored novaya articles have no title, and thus will return lower relevance scores. Returned text will be in escaped unicode instead of the original Cyrillic text. 

**HTTP Request**

`GET api/multi_novaya`

**Parameters:**
- search_string: Text separated by underscores. Stop words and dangerous words are removed from a maintained list before usage in SQL. If no value is specified, does not use text-based search.
- min_relevancy: The minimum relevance score for an article to show up in search results. If no value is specified, defaults to 1.
- time_start: The earliest point an article could have been published to return in the search results. If no value is specified, pulls article from earliest point.
- time_end: The latest point an article could have been published to return in the search results. If no value is specified, pulls articles up until latest point.
- item_limit: The maximum number of articles to return in the search. If no value specified, defaults to 500.

**Example**

Input: `http://www.___.com/api/multi_novaya?limit=1`

Output:

```
{
    "articles": [
        {
            "author": "\u00d0\u0091\u00d0\u00b5\u00d0\u00b7 \u00d0\u00b0\u00d0\u00b2\u00d1\u0082\u00d0\u00be\u00d1\u0080\u00d0\u00b0\n", 
            "category": "Economy", 
            "content": "\u00d0\u0098 \u00d0\u00bf\u00d0\u00be\u00d1\u0081\u00d0\u00bb\u00d0\u00b5\u00d0\u00b4\u00d0\u00bd\u00d0\u00b5\u00d0\u00b5. \u00d0\u0097\u00d0\u00b0 \u00d0\u00bc\u00d0\u00bd\u00d0\u00be\u00d0\u00b3\u00d0\u00b8\u00d0\u00b5 \u00d0\u00b3\u00d0\u00be\u00d0\u00b4\u00d1\u008b \u00d1\u0080\u00d1\u0083\u00d0\u00ba\u00d0\u00be\u00d0\u00b2\u00d0\u00be\u00d0\u00b4\u00d1\u0081\u00d1\u0082\u00d0\u00b2\u00d0\u00be \u00c2\u00ab\u00d0\u00a2\u00d0\u00be\u00d0\u00bb\u00d1\u008c\u00d1\u008f\u00d1\u0082\u00d1\u0082\u00d0\u00b8\u00d0\u00b0\u00d0\u00b7\u00d0\u00be\u00d1\u0082\u00d0\u00b0\u00c2\u00bb \u00d0\u00bd\u00d0\u00b5 \u00d0\u00bf\u00d0\u00be\u00d0\u00bb\u00d1\u0083\u00d1\u0087\u00d0\u00b8\u00d0\u00bb\u00d0\u00be \u00d0\u00bd\u00d0\u00b8 \u00d0\u00be\u00d0\u00b4\u00d0\u00bd\u00d0\u00be\u00d0\u00b3\u00d0\u00be \u00d0\u00be\u00d1\u0084\u00d0\u00b8\u00d1\u0086\u00d0\u00b8\u00d0\u00b0\u00d0\u00bb\u00d1\u008c\u00d0\u00bd\u00d0\u00be\u00d0\u00b3\u00d0\u00be \u00d0\u00be\u00d1\u0082\u00d0\u00b2\u00d0\u00b5\u00d1\u0082\u00d0\u00b0 \u00d0\u00bd\u00d0\u00b0 \u00d1\u0081\u00d0\u00b2\u00d0\u00be\u00d0\u00b8 \u00d0\u00be\u00d0\u00b1\u00d1\u0080\u00d0\u00b0\u00d1\u0089\u00d0\u00b5\u00d0\u00bd\u00d0\u00b8\u00d1\u008f \u00d0\u00b2 \u00d0\u00be\u00d1\u0080\u00d0\u00b3\u00d0\u00b0\u00d0\u00bd\u00d1\u008b \u00d1\u0084\u00d0\u00b5\u00d0\u00b4\u00d0\u00b5\u00d1\u0080\u00d0\u00b0\u00d0\u00bb\u00d1\u008c\u00d0\u00bd\u00d0\u00be\u00d0\u00b9 \u00d0\u00b8 \u00d0\u00ba\u00d1\u0080\u00d0\u00b0\u00d0\u00b5\u00d0\u00b2\u00d0\u00be\u00d0\u00b9 \u00d0\u00b8\u00d1\u0081\u00d0\u00bf\u00d0\u00be\u00d0\u00bb\u00d0\u00bd\u00d0\u00b8\u00d1\u0082\u00d0\u00b5\u00d0\u00bb\u00d1\u008c\u00d0\u00bd\u00d0\u00be\u00d0\u00b9 \u00d0\u00b2\u00d0\u00bb\u00d0\u00b0\u00d1\u0081\u00d1\u0082\u00d0\u00b8. \u00d0\u0098\u00d0\u00bd\u00d1\u0082\u00d0\u00b5\u00d1\u0080\u00d0\u00b5\u00d1\u0081\u00d0\u00bd\u00d0\u00b0\u00d1\u008f \u00d1\u0081\u00d0\u00b8\u00d0\u00bd\u00d1\u0085\u00d1\u0080\u00d0\u00be\u00d0\u00bd\u00d0\u00bd\u00d0\u00be\u00d1\u0081\u00d1\u0082\u00d1\u008c, \u00d0\u00bd\u00d0\u00b5 \u00d0\u00bf\u00d1\u0080\u00d0\u00b0\u00d0\u00b2\u00d0\u00b4\u00d0\u00b0 \u00d0\u00bb\u00d0\u00b8?\n", 
            "kp": 1, 
            "original_post": "\u00d0\u00ad\u00d1\u0082\u00d0\u00be\u00d1\u0082 \u00d0\u00bc\u00d0\u00b0\u00d1\u0082\u00d0\u00b5\u00d1\u0080\u00d0\u00b8\u00d0\u00b0\u00d0\u00bb \u00d0\u00b2\u00d1\u008b\u00d1\u0088\u00d0\u00b5\u00d0\u00bb \u00d0\u00b2 \u00e2\u0084\u0096 143 \u00d0\u00be\u00d1\u0082 20 \u00d0\u00b4\u00d0\u00b5\u00d0\u00ba\u00d0\u00b0\u00d0\u00b1\u00d1\u0080\u00d1\u008f 2010 \u00d0\u00b3.", 
            "pub_date": "2010-12-20", 
            "relevance": 0, 
            "ret_date": "2019-01-24"
        }
    ], 
    "count": 1
}
```

## Free_Weibo
Provides search through the database of collected Free Weibo posts. If no parameters are specified, 500 posts will be returned. Note that stored weibo posts have no title, and thus will return lower relevance scores. Returned text will be in escaped unicode, and include raw HTML from the weibo post.

**HTTP Request**

`GET /api/multi_weibo`

**Parameters:**
- search_string: Text separated by underscores. Stop words and dangerous words are removed from a maintained list before usage in SQL. If no value is specified, does not use text-based search. e.g - 'Donald_Trump_Wall'
- min_relevancy: The minimum relevance score for an article to show up in search results. If no value is specified, defaults to 1.
- time_start: The earliest point an article could have been published to return in the search results. If no value is specified, pulls article from earliest point.
- time_end: The latest point an article could have been published to return in the search results. If no value is specified, pulls articles up until latest point.
- item_limit: The maximum number of articles to return in the search. If no value specified, defaults to 500.

**Example:**

Input: `GET http://www.___.com/api/multi_weibo?item_limit=1`

Output: 
```
{
  "count": 1,
  "posts": [
    {
      "bag_of_words": null,
      "confidence": 1,
      "weibo_id": "4209652352950309",
      "ret_date": "2018-02-21 22:47:13",
      "content": "<a href=\"/weibo/%40%E5%96%B7%E5%9A%8F%E7%BD%91%E9%93%82%E7%A8%8B\">\\u55b7\\u568f\\u7f51\\u94c2\\u7a0b</a>\\uff1a//<a href=\"/weibo/%40%E4%BA%92%E8%81%94%E7%BD%91%E7%9A%84%E9%82%A3%E7%82%B9%E4%BA%8B\">@\\u4e92\\u8054\\u7f51\\u7684\\u90a3\\u70b9\\u4e8b</a>:[\\u6316\\u9f3b]//<a href=\"/weibo/%40%E5%93%8D%E9%A9%AC\">@\\u54cd\\u9a6c</a>:\\u5c4c\\u70b8\\u4e86 //<a href=\"/weibo/%40%E6%8C%89%E7%85%A7%E5%9F%BA\">@\\u6309\\u7167\\u57fa</a>xb7\\u672cxb7\\u6cd5-\\u9ad8\\u68a8\\u592a\\u90ce:\\u4e3a\\u4e86\\u52a0\\u901f<span style=\"color:red\">\\u5feb\\u89c6\\u9891</span>\\u6b7b\\u4ea1\\uff0c\\u800c\\u4e0a\\u4f20\\u8272\\u60c5\\u548c\\u90a3\\u4e2a\\u7537\\u4eba\\u7684\\u89c6\\u9891\\u7684\\u884c\\u4e3a\\u4e5f\\u662f\\u6709\\u75c5[\\u5410] <a href=\"http://t.cn/RRFmYhj\" target=\"_BLANK\">http://t.cn/RRFmYhj</a>",
      "relevance": 0,
      "kp": 1,
      "lang_detected": "zh",
      "pub_date": "2018-02-21 00:06:00"
    }
  ]
}
```

## corpora_metrics
Provides quick and efficient access to content metrics.

**Parameters:**
None

**Example:**

Input: `http://www.___.com/api/corpora_metrics`

Output: 
```
{
  "rss_count": 32,
  "freeweibo_topic_count": 1594983,
  "novaya_count": 2353,
  "freeweibo_count": 5026,
  "article_count": 86169
}
```
