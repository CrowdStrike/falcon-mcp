# Regular Expression Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-regular-expression.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Regular Expression Query Functions

LogScale's regex related functions make use of the LogScale regular expression engine. See [Regular Expression-based Field Extraction](syntax-fields.html#syntax-fields-extracting "Regular Expression-based Field Extraction") for more information on writing regular expressions. 

**Table: Regular Expression Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`array:regex(array, [flags], regex)`](functions-array-regex.html "array:regex\(\)")| [_`array`_](functions-array-regex.html#query-functions-array-regex-array)|  |  Checks whether the given pattern matches any of the values of the array and excludes the event from the search result.   
[`regex([field], [flags], [limit], regex, [repeat], [strict])`](functions-regex.html "regex\(\)")| [_`regex`_](functions-regex.html#query-functions-regex-regex)|  |  Extracts new fields using a regular expression.   
[`replace([as], [field], [flags], regex, [replacement], [with])`](functions-replace.html "replace\(\)")| [_`regex`_](functions-replace.html#query-functions-replace-regex)|  |  Replaces each substring that matches given regular expression with given replacement.   
[`splitString([as], by, [field], [index])`](functions-splitstring.html "splitString\(\)")| [_`field`_](functions-splitstring.html#query-functions-splitstring-field)|  |  Splits a string by specifying a regular expression by which to split.
