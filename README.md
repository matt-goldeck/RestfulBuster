# RestfulBuster: A simple RESTful API in Flask
Provides easy access and search through content on the NetSci Lab database. An evolution of my very crudely constructed CensorBuster interface in Django used prior.

Works in conjuction with Apollo -> https://github.com/leberkc/nlp-news-aggregator

More information information can be found -> www.netsci.montclair.edu 

# Basic Gist
A collection of content useful in studies of government web censorship is either manually or automatically extracted and then stored on a MySQL server at Montclair State University. This application aims to provide easy, RESTful access to the aforementioned content. As of right now this content, broadly speaking, is:
 - RSS Articles: Articles scraped from RSS feeds in both their original text form and a processed 'bag-of-words'. Associated metrics are included.
 - FreeWeibo Content: Posts and topics that have been determined to have been censored by the FreeWeibo Project. Stored similarly to articles.
 - More, eventually.
 
Search through this content works very crudely. I ~~stole~~ was inspired by some common blog search algorithms that look through the content of each post and assign points based on whether or not the whole query or parts of the query are present. As news articles and social media posts are very similiar to blogs, I felt this suited the need rather well. Relevance points are assigned very unscientifically to the standard of "had a good gut feeling about it." They are described in this table:

Match | Score
------|------
Complete phrase in the title | 10
Complete phrase in the content | 7
Keyword appearance in the title | 5
Keyword appearance in the content | 3

As of right now, search is only available through articles, though this feature should be flexible enough to expand onto any other content with the right amount of work.
 

# Endpoints
There are currently **3** endpoints:

## specific_article
Provides access to a single article, specified by the KP parameter. Very straightforward.

**Parameters:**
- kp: The unique primary key assigned to the article. 

**Example:**

Input: 

`http://www.___.com/RestfulBuster/spec_article?kp=1`

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
## multi_article
Multiple parameters allow customizable search through the database of collected articles. If no parameters are specified, all articles will be returned.

**Parameters:**

- search_string: Text separated by underscores. Stop words and dangerous words are removed from a maintained list before usage in SQL. If no value is specified, does not use text-based search.
- min_relevancy: The minimum relevance score for an article to show up in search results. If no value is specified, defaults to 1.
- category: The category of RSS feed this article came from. Matched against the rss table then joined with the article_source table. Only one category can be specified. If no value is specified, defaults to all categories. 
- time_start: The earliest point an article could have been published to return in the search results. If no value is specified, pulls article from earliest point.
- time_end: The latest point an article could have been published to return in the search results. If no value is specified, pulls articles up until latest point.
- article_limit: The maximum number of articles to return in the search. If no value specified, defaults to 500.

**Example:**

Input:
`http://www.____.com/RestfulBuster/multi_article?search_string=toast_college_student&time_end=19960101&time_start=20180101&min_relevancy=3&article_limit=1&category=Domestic`
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

## corpora_metrics
Provides quick and efficient access to content metrics.

**Parameters:**
None

**Example:**

Input: `http://www.___.com/RestfulBuster/corpora_metrics`

Output: 
```
{
    "article_count": 78957,
    "freeweibo_count": 56451,
    "freeweibo_topic_count": 167895,
    "rss_count": 34
}
```

