# RestfulBuster: A simple RESTful API in Flask
Provides easy access and search through content on the NetSci Lab database. An evolution of my very crudely constructed CensorBuster interface in Django used prior.

Works in conjuction with these projects: x, y, z

More information information can be found at: www.netsci.montclair.edu 

# Basic Gist
A collection of content useful in studies of government web censorship is either manually or automatically extracted and then stored on a MySQL server at Montclair State University. As of right now this content, broadly speaking, is:
 - RSS Articles: Articles scraped from RSS feeds in both their original text form and a processed 'bag-of-words'. Associated metrics are included.
 - FreeWeibo Content: Posts and topics that have been determined to have been censored by the FreeWeibo Project. Stored similarly to articles.
 - More, eventually.
 
Search through this content works very crudely. I ~~stole~~ was inspired by some common blog search algorithms that look through the content of each post and assign points based on whether or not the whole query or parts of the query are present. As news articles and social media posts are very similiar to blogs, I felt this worked rather well. The points are assigned very unscientifically in a manner that felt right to me. 

As of right now, search is only available through articles, though this feature should be flexible enough to expand onto any other content with the right amount of work.
 

# Endpoints
There are currently **3** endpoints:

## specific_article
Provides access to a single article, specified by the KP parameter. Very straightforward.

**Parameters:**
- kp: The unique primary key assigned to the article. 

**Example:**

Input: 

`www.___.com/RestfulBuster/spec_article?kp=1`

Output: 
```
[
    {
        "bag_of_words": "local, college, student, toast, morning, authorities, report, hours, morning, matthew, goldeck hours, variety, bread, incident, confirmed, sources, matreport, Matthew, Goldeck, New, Jersey, produced, slices, toasted, bread, parent's, kitchen, variety, incident, sources,, report prefers, pumpernickel, check, day, updates",
        "confidence": 0.363515,
        "content": "MattNews: A local college student made toast this morning. Authorities report that sometime between the hours of 7 and 9 in the morning, Matthew Goldeck of New Jersey produced two slices of toasted bread in his parent's kitchen. While the exact variety of bread used in the incident has not been confirmed, sources close to the matter report Matthew prefers pumpernickel. Check back throughout the day for updates.",
        "kp": 1996,
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
]
```
## Multiple Articles
Multiple parameters allow customizable search through the database of collected articles. 

**Parameters:**

- search_string: Text separated by underscores. Stop words and dangerous words are removed from a maintained list before usage in SQL. 
**URL:** www.xyz.com/RestfulBuster/multi_article



