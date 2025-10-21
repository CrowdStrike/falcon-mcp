# Filtering Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-filter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Filtering Query Functions

Filter functions allow you to filter events or event data based on whether the query matches the filter. For example: 

logscale
    
    
    **in(name,values=["datasource-count"])**

Returns all events where the name field equals datasource-count. 

Filter functions can also be negated, for example, filter the events that do not match the given filter. For example: 

logscale
    
    
    **!in(name,values=["datasource-count"])**

Returns all events where the name field does not equal datasource-count. 

### Note

All the functions in the [Filtering Query Functions](functions-filter.html#table_functions-filtering "Table: Filtering Query Functions") table are negatable except [`sample()`](functions-sample.html "sample\(\)"). 

**Table: Filtering Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`array:contains(array, value)`](functions-array-contains.html "array:contains\(\)")| [_`array`_](functions-array-contains.html#query-functions-array-contains-array)|  |  Checks whether the given value matches any of the values of the array and excludes the event if no value matches.   
[`array:exists(array, condition, [var])`](functions-array-exists.html "array:exists\(\)")| [_`array`_](functions-array-exists.html#query-functions-array-exists-array)|  |  Filters events based on whether the given array contains an element that satisfies a given condition (based on the array argument). Recommended for flat arrays. Does not work on nested arrays — use [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") instead.   
[`array:filter(array, [asArray], function, [var])`](functions-array-filter.html "array:filter\(\)")| [_`array`_](functions-array-filter.html#query-functions-array-filter-array)|  |  Drops entries from the input array using the given filtering function.   
[`array:regex(array, [flags], regex)`](functions-array-regex.html "array:regex\(\)")| [_`array`_](functions-array-regex.html#query-functions-array-regex-array)|  |  Checks whether the given pattern matches any of the values of the array and excludes the event from the search result.   
[`cidr([column], field, [file], [negate], [subnet])`](functions-cidr.html "cidr\(\)")| [_`field`_](functions-cidr.html#query-functions-cidr-field)|  |  Filters events using CIDR subnets.   
[`in(field, [ignoreCase], values)`](functions-in.html "in\(\)")| [_`field`_](functions-in.html#query-functions-in-field)|  |  Filters records by values where field is in given values.   
[`match([column], field, file, [glob], [ignoreCase], [include], [mode], [nrows], [strict], nrows)`](functions-match.html "match\(\)")| [_`file`_](functions-match.html#query-functions-match-file)|  |  Searches text using a CSV or JSON file and can enhance entries.   
[`regex([field], [flags], [limit], regex, [repeat], [strict])`](functions-regex.html "regex\(\)")| [_`regex`_](functions-regex.html#query-functions-regex-regex)|  |  Extracts new fields using a regular expression.   
[`sample([field], [percentage])`](functions-sample.html "sample\(\)")| [_`percentage`_](functions-sample.html#query-functions-sample-percentage)|  |  Samples the event stream.   
[`selfJoinFilter(field, [prefilter], where)`](functions-selfjoinfilter.html "selfJoinFilter\(\)")| [_`field`_](functions-selfjoinfilter.html#query-functions-selfjoinfilter-field)|  |  Runs query to determine IDs, and then gets all events containing one of them.   
[`test(expression)`](functions-test.html "test\(\)")| [_`expression`_](functions-test.html#query-functions-test-expression)|  |  Evaluates boolean expression and filters events.   
[`text:contains(string, substring)`](functions-text-contains.html "text:contains\(\)")| [_`string`_](functions-text-contains.html#query-functions-text-contains-string)|  |  Tests if a specific substring is present within a given string.   
[`text:endsWith(string, substring)`](functions-text-endswith.html "text:endsWith\(\)")| [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string)|  |  Tests if a specific substring is present at the end of a given string.   
[`text:startsWith(string, substring)`](functions-text-startswith.html "text:startsWith\(\)")| [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string)|  |  Tests if a specific substring is present at the start of a given string.   
[`wildcard([field], [ignoreCase], [includeEverythingOnAsterisk], pattern)`](functions-wildcard.html "wildcard\(\)")| [_`pattern`_](functions-wildcard.html#query-functions-wildcard-pattern)|  |  Performs a wildcard pattern search with optional case insensitivity.
