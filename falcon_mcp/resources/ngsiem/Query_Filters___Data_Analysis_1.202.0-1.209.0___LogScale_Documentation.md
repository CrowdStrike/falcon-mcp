# Query Filters | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-filters.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Query Filters

LogScale query filters enable powerful search capabilities through free text matching, field-specific filters, and regular expressions, with each type offering distinct ways to find and filter event data. The documentation covers the syntax and usage of these three filter types, including how multiple filters can be combined with implicit AND operations, along with important considerations for performance and field extraction when using different filtering methods. 

Query filters allow you to search LogScale with filters using [free text](syntax-filters.html#syntax-filters-grepping "Free-Text Filters"), [field matches](syntax-filters.html#syntax-filters-field "Field Filters"), and [regular expressions](syntax-filters.html#syntax-filters-regex "Regular Expression Filters"). 

A filter is a less general kind of expression compared to an expression. Neither is a subset of the other, but `Filter` is particularly quirky: 

Implicit `AND` is supported in the `Filter` production so be aware that this: 

logscale Syntax
    
    
    foo < 42 + 3

means: 

logscale Syntax
    
    
    (foo < 42) AND "*+*" AND "*3*"

Essentially, two expressions are considered to be logically combined with an `AND` so that: 

logscale
    
    
    src="client" ip="127.0.0.1"

Matches both filter expressions, (for example both a client and localhost address). 

The above implies the pipe in the expression, so the above is identical to: 

logscale
    
    
    src="client"
    | ip="127.0.0.1"

For more information on the precise grammar for filters, see [Filters](https://library.humio.com/lql-grammar/syntax-grammar-guide-subset.html#syntax-grammar-guide-subset-filters). 

### Free-Text Filters

The most basic query in LogScale is to search for a particular string in any field of events. All fields (except for the special [@id](searching-data-event-fields.html#searching-data-event-fields-metadata-id), [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp), [@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp) fields and the [tag fields](https://library.humio.com/training/training-fc-ingestion.html#training-fc-ingestion-event-tags)) are searched, including [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring). 

Free-text filters operate on the fields in the events that are present at the start of the pipeline when performing a search. Free-text search does not take into account any fields added or removed within the pipeline. 

Free-text searches are only supported _before_ an aggregate. A free-text search after the first aggregate function refers to any text filter that is not specific to a field and appears after the query's first aggregate function. For instance, this example syntax with a free-text search after an aggregate function is not valid: 

Invalid Example for Demonstration - DO NOT USE 

logscale
    
    
    "Lorem ipsum dolor" 
    | tail(200)         
    | "sit amet, consectetur"

To work around this issue, you can: 

  * Move the free-text search in front of the first aggregate function. 

  * Search specifically in the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field. 




If you know the field that contains the value you're searching for, it's best to search that particular field. The field may have been added by either the log shipper or the parser, and the information might not appear in the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field. 

When a free-text search is applied in a parser this differs; the event is processed as it is present at the point where the free-text search occurs. LogScale recommends using [Field Filters](syntax-filters.html#syntax-filters-field "Field Filters") whenever possible within a parser to avoid ambiguous matches. 

Free-text search does not specify the order in which fields are searched. When not extracting fields, the order in which fields are checked is not relevant as any match will let the event pass the filter. 

But when extracting fields using a regular expression, matches can yield non-deterministic extracted fields. To make extracted fields be the same if a match was also possible in the older versions, LogScale prefers a match on [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) before trying other fields when extracting fields. 

### Note

You can perform more complex regular expression searches on all fields of an event by using the [`regex()`](functions-regex.html "regex\(\)") function or the [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") regex syntax. 

Query |  Description   
---|---  
`foo` |  Find all events matching `foo` in any field of the events. Without a field specification, the text is treated as if it has a leading and trailing wildcard. For example `*foo*`  
`"foo bar"` |  Use quotes if the search string contains white spaces or special characters, or is a keyword. Without a field specification, the text is treated as if it has a leading and trailing wildcard. For example `"*foo*"`  
`"msg:\"welcome\" "` |  You can include quotes in the search string by escaping them with backslashes.   
  
You can also use a regular expression on all fields. To do this, write the regular expression, for example [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters"): 

Query |  Description   
---|---  
`/foo/` |  Find all events matching `foo` in any field of the events.   
`/foo/i` |  Find all events matching `foo` ignoring case.   
  
### Field Filters

Besides the [free-text filters](syntax-filters.html#syntax-filters-grepping "Free-Text Filters"), you can also query specific event fields, both as text and as numbers. 

Query |  Description   
---|---  
`url = *login*` |  The `url` field contains `login`. You can use `*` as a wild card.   
`user = *Turing` |  The `user` field ends with Turing.   
`user = "Alan Turing"` |  The `user` field equals Alan Turing.   
`user != "Alan Turing"` |  The `user` field does not equal Alan Turing.   
`url != *login*` |  The url field does not contain `login`.   
`user = *` |  Match events that have the field `user`.   
`user != *` |  Match events that do not have the field `user`.   
`name = ""` |  Match events that have a field called `name` but with the empty string as value.   
`user= "Alan Turing"` |  You do not need to put spaces around operators (for example, `=` or `!=`).   
  
### Regular Expression Filters

In addition to globbing (`*` appearing in match strings) you can match fields using regular expressions. 

To use a regular expression, enclose the regular expression in two forward slashes. For example: 

logscale
    
    
    /regex/

The use of a regex in this syntax is similar to using the [`regex()`](functions-regex.html "regex\(\)"). There are some differences between [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") and [`regex()`](functions-regex.html "regex\(\)") operations: 

  * [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") searches: 

    * [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring)

    * All extracted/parsed fields 

  * `field = /regex/` searches: 

    * Only the specified field using the qualified regular expression 

  * [`regex()`](functions-regex.html "regex\(\)") searches: 

    * a single field (default is [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring)) 




### Important

The different regex syntax operations are significantly different in performance: the [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") searching over all fields is slower compared to using either [`regex()`](functions-regex.html "regex\(\)") or [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") that search on a single, specific field instead. 

Query |  Description   
---|---  
`url = /login/` |  The url field contains `login`.   
`user = /Turing$/` |  The user field ends with `Turing`.   
`loglevel = /error/i` |  The loglevel field matches `error` case insensitively; for example, it could be `Error`, `ERROR` or `error`.   
`/user with id (?<id>\S+) logged in/ | top(id)` |  The user id is extracted into a field named id at search time. The id is then used in the top function to find the users that logged in the most.   
  
Certain functions can also be used to filter events. For a list of these functions, see [Filtering Query Functions](functions-filter.html "Filtering Query Functions").
