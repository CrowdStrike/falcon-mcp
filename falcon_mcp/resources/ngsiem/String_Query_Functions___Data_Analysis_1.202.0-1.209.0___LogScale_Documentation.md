# String Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-string.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## String Query Functions

LogScale's string functions allow for string data within events to be extracted, combined or modified. 

**Table: String Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`concat([as], field)`](functions-concat.html "concat\(\)")| [_`field`_](functions-concat.html#query-functions-concat-field)|  |  Concatenates the values of a list of fields into a value in a new field.   
[`concatArray([as], field, [from], [prefix], [separator], [suffix], [to])`](functions-concatarray.html "concatArray\(\)")| [_`field`_](functions-concatarray.html#query-functions-concatarray-field)|  |  Concatenates values of all fields with same name and an array suffix into a new field.   
[`length([as], field)`](functions-length.html "length\(\)")| [_`field`_](functions-length.html#query-functions-length-field)|  |  Computes the number of characters in a string field.   
[`lowercase(field, [include], [locale])`](functions-lowercase.html "lowercase\(\)")| [_`field`_](functions-lowercase.html#query-functions-lowercase-field)|  |  Changes field name or content to lowercase for parsers.   
[`regex([field], [flags], [limit], regex, [repeat], [strict])`](functions-regex.html "regex\(\)")| [_`regex`_](functions-regex.html#query-functions-regex-regex)|  |  Extracts new fields using a regular expression.   
[`replace([as], [field], [flags], regex, [replacement], [with])`](functions-replace.html "replace\(\)")| [_`regex`_](functions-replace.html#query-functions-replace-regex)|  |  Replaces each substring that matches given regular expression with given replacement.   
[`splitString([as], by, [field], [index])`](functions-splitstring.html "splitString\(\)")| [_`field`_](functions-splitstring.html#query-functions-splitstring-field)|  |  Splits a string by specifying a regular expression by which to split.   
[`stripAnsiCodes([as], field)`](functions-stripansicodes.html "stripAnsiCodes\(\)")| [_`field`_](functions-stripansicodes.html#query-functions-stripansicodes-field)|  |  Removes ANSI color codes and movement commands.   
[`text:length([as], string)`](functions-text-length.html "text:length\(\)")| [_`string`_](functions-text-length.html#query-functions-text-length-string)| **added in 1.207**|  Computes the length of a string.   
[`text:positionOf([as], [begin], character, [occurrence], string)`](functions-text-positionof.html "text:positionOf\(\)")| [_`string`_](functions-text-positionof.html#query-functions-text-positionof-string)| **added in 1.207**|  Computes the position of a given character or substring within a string.   
[`text:substring([as], [begin], [end], string)`](functions-text-substring.html "text:substring\(\)")| [_`string`_](functions-text-substring.html#query-functions-text-substring-string)| **added in 1.207**|  Extracts a substring from a string given a pair of positions into the string.   
[`tokenHash([as], field)`](functions-tokenhash.html "tokenHash\(\)")| [_`field`_](functions-tokenhash.html#query-functions-tokenhash-field)|  |  Calculates a hash by tokenizing the input string (split by spaces), creating a hash for each token and then added the result together. This generates the same hash value, even if the order of the individual values in the source string is different.
