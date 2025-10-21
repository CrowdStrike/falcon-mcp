# Formatting Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-formatting.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Formatting Query Functions

LogScale's formatting functions allow different data types to be formatted and manipulated, either for further processing or make things more human-readable. 

**Table: Formatting Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`default(field, [replaceEmpty], value)`](functions-default.html "default\(\)")| [_`value`_](functions-default.html#query-functions-default-value)|  |  Creates a field to given parameter and given value.   
[`format([as], field, format, [timezone])`](functions-format.html "format\(\)")| [_`format`_](functions-format.html#query-functions-format-format)|  |  Formats a string using printf-style.   
[`formatDuration([as], field, [from], [precision])`](functions-formatduration.html "formatDuration\(\)")| [_`field`_](functions-formatduration.html#query-functions-formatduration-field)|  |  Formats a duration into a more readable string.   
[`formatTime(as, [field], format, [locale], [timezone], [unit])`](functions-formattime.html "formatTime\(\)")| [_`format`_](functions-formattime.html#query-functions-formattime-format)|  |  Formats a string according to `strftime()`.   
[`json:prettyPrint([as], [field], [step], [strict])`](functions-json-prettyprint.html "json:prettyPrint\(\)")| [_`field`_](functions-json-prettyprint.html#query-functions-json-prettyprint-field)|  |  More readable output to a JSON field.   
[`lower([as], field, [locale], [type])`](functions-lower.html "lower\(\)")| [_`field`_](functions-lower.html#query-functions-lower-field)|  |  Changes text of a given string field to lower case letters.   
[`lowercase(field, [include], [locale])`](functions-lowercase.html "lowercase\(\)")| [_`field`_](functions-lowercase.html#query-functions-lowercase-field)|  |  Changes field name or content to lowercase for parsers.   
[`upper([as], field, [locale])`](functions-upper.html "upper\(\)")| [_`field`_](functions-upper.html#query-functions-upper-field)|  |  Changes contents of a string field to upper case letters.   
[`urlDecode([as], field)`](functions-urldecode.html "urlDecode\(\)")| [_`field`_](functions-urldecode.html#query-functions-urldecode-field)|  |  URL-decodes the contents of a string field.   
[`urlEncode([as], field, [type])`](functions-urlencode.html "urlEncode\(\)")| [_`field`_](functions-urlencode.html#query-functions-urlencode-field)|  |  URL encodes the contents of a string field.   
[`writeJson([as], [field])`](functions-writejson.html "writeJson\(\)")| [_`field`_](functions-writejson.html#query-functions-writejson-field)|  |  Writes data, including fields, as a JSON object.
