# Data Manipulation Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-data-manipulation.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Data Manipulation Query Functions

LogScale's event and data manipulation functions allow event creation, modification and data manipulation of events and fields within the event. 

**Table: Data Manipulation Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`accumulate([current], function)`](functions-accumulate.html "accumulate\(\)")| [_`function`_](functions-accumulate.html#query-functions-accumulate-function)|  |  Applies an aggregation function cumulatively to a sequence of events.   
[`array:append(array, values)`](functions-array-append.html "array:append\(\)")| [_`array`_](functions-array-append.html#query-functions-array-append-array)|  |  Appends single or multiple values to an array, or creates a new array if it does not already exist.   
[`array:contains(array, value)`](functions-array-contains.html "array:contains\(\)")| [_`array`_](functions-array-contains.html#query-functions-array-contains-array)|  |  Checks whether the given value matches any of the values of the array and excludes the event if no value matches.   
[`array:dedup(array, [asArray])`](functions-array-dedup.html "array:dedup\(\)")| [_`array`_](functions-array-dedup.html#query-functions-array-dedup-array)|  |  [`array:dedup()`](functions-array-dedup.html "array:dedup\(\)") removes duplicate elements from an array. The ordering of the first occurrence of each unique element is preserved.   
[`array:exists(array, condition, [var])`](functions-array-exists.html "array:exists\(\)")| [_`array`_](functions-array-exists.html#query-functions-array-exists-array)|  |  Filters events based on whether the given array contains an element that satisfies a given condition (based on the array argument). Recommended for flat arrays. Does not work on nested arrays — use [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") instead.   
[`array:filter(array, [asArray], function, [var])`](functions-array-filter.html "array:filter\(\)")| [_`array`_](functions-array-filter.html#query-functions-array-filter-array)|  |  Drops entries from the input array using the given filtering function.   
[`array:reduceAll(array, function, var)`](functions-array-reduceall.html "array:reduceAll\(\)")| [_`array`_](functions-array-reduceall.html#query-functions-array-reduceall-array)|  |  Computes a value from all events and array elements of the specified array.   
[`array:reduceColumn(array, [as], function, var)`](functions-array-reducecolumn.html "array:reduceColumn\(\)")| [_`array`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-array)|  |  Computes an aggregate value for each array element with the same index.   
[`array:rename(array, asArray)`](functions-array-rename.html "array:rename\(\)")| [_`array`_](functions-array-rename.html#query-functions-array-rename-array)|  |  Takes the name of an array and renames all fields of this array.   
[`array:sort(array, [asArray], [order], [type])`](functions-array-sort.html "array:sort\(\)")| [_`array`_](functions-array-sort.html#query-functions-array-sort-array)|  |  Sorts the elements of an array of values using the given sorting data type and order.   
[`array:union(array, [as])`](functions-array-union.html "array:union\(\)")| [_`array`_](functions-array-union.html#query-functions-array-union-array)|  |  Determines the set union of array values over input events.   
[`bitfield:extractFlags(field, [onlyTrue], output)`](functions-bitfield-extractflags.html "bitfield:extractFlags\(\)")|  |  |  Interprets an integer as a bit field and extracts the specified flags.   
[`bitfield:extractFlagsAsArray([asArray], field, flagNames)`](functions-bitfield-extractflagsasarray.html "bitfield:extractFlagsAsArray\(\)")|  |  |  Interprets an integer as a bit field and extracts the specified flags. Information is returned as an array, listed in ascending order, from lowest bit to highest bit.   
[`bitfield:extractFlagsAsString([as], field, flagNames, [separator])`](functions-bitfield-extractflagsasstring.html "bitfield:extractFlagsAsString\(\)")|  |  |  Interprets an integer as a bit field and extracts the specified flags. Information is returned as a string, listed in ascending order, from lowest bit to highest bit.   
[`coalesce([as], expressions, [ignoreEmpty])`](functions-coalesce.html "coalesce\(\)")| [_`expressions`_](functions-coalesce.html#query-functions-coalesce-expressions)|  |  Selects the value of the first expression from a list of expressions   
[`concat([as], field)`](functions-concat.html "concat\(\)")| [_`field`_](functions-concat.html#query-functions-concat-field)|  |  Concatenates the values of a list of fields into a value in a new field.   
[`concatArray([as], field, [from], [prefix], [separator], [suffix], [to])`](functions-concatarray.html "concatArray\(\)")| [_`field`_](functions-concatarray.html#query-functions-concatarray-field)|  |  Concatenates values of all fields with same name and an array suffix into a new field.   
[`copyEvent(type)`](functions-copyevent.html "copyEvent\(\)")| [_`type`_](functions-copyevent.html#query-functions-copyevent-type)|  |  Duplicates an event so that the pipeline will see both events.   
[`drop(fields)`](functions-drop.html "drop\(\)")| [_`fields`_](functions-drop.html#query-functions-drop-fields)|  |  Removes specified fields from each event.   
[`dropEvent()`](functions-dropevent.html "dropEvent\(\)")|  |  |  Drops completely an event in parser pipeline to stop it from being ingested.   
[`eval()`](functions-eval.html "eval\(\)")|  |  |  Creates a new field by evaluating the provided expression.   
[`format([as], field, format, [timezone])`](functions-format.html "format\(\)")| [_`format`_](functions-format.html#query-functions-format-format)|  |  Formats a string using printf-style.   
[`getField([as], source)`](functions-getfield.html "getField\(\)")|  |  |  Reads dynamically-named fields that are computed from an expression.   
[`json:prettyPrint([as], [field], [step], [strict])`](functions-json-prettyprint.html "json:prettyPrint\(\)")| [_`field`_](functions-json-prettyprint.html#query-functions-json-prettyprint-field)|  |  More readable output to a JSON field.   
[`lowercase(field, [include], [locale])`](functions-lowercase.html "lowercase\(\)")| [_`field`_](functions-lowercase.html#query-functions-lowercase-field)|  |  Changes field name or content to lowercase for parsers.   
[`neighbor([direction], [distance], include, [prefix])`](functions-neighbor.html "neighbor\(\)")| [_`include`_](functions-neighbor.html#query-functions-neighbor-include)|  |  Allows access to fields from a single neighboring event in a sequence.   
[`parseCEF([field], [headerprefix], [keeplabels], [labelprefix], [prefix])`](functions-parsecef.html "parseCEF\(\)")| [_`field`_](functions-parsecef.html#query-functions-parsecef-field)|  |  Parses CEF version 0.x encoded messages.   
[`parseCsv(columns, [delimiter], [excludeEmpty], field, [trim])`](functions-parsecsv.html "parseCsv\(\)")| [_`field`_](functions-parsecsv.html#query-functions-parsecsv-field)|  |  Parses a CSV-encoded field into known columns.   
[`parseHexString([as], [charset], field)`](functions-parsehexstring.html "parseHexString\(\)")| [_`field`_](functions-parsehexstring.html#query-functions-parsehexstring-field)|  |  Parses input from hex encoded bytes, decoding resulting bytes as a string.   
[`parseJson([exclude], [excludeEmpty], field, [handleNull], [include], [prefix], [removePrefixes])`](functions-parsejson.html "parseJson\(\)")| [_`field`_](functions-parsejson.html#query-functions-parsejson-field)|  |  Parses specified fields as JSON.   
[`parseLEEF([delimiter], [field], [headerprefix], [keeplabels], [labelprefix], [parsetime], [prefix], [timezone])`](functions-parseleef.html "parseLEEF\(\)")| [_`field`_](functions-parseleef.html#query-functions-parseleef-field)|  |  Parses LEEF version 1.0 and 2.0 encoded messages.   
[`partition(condition, function, [split])`](functions-partition.html "partition\(\)")| [_`function`_](functions-partition.html#query-functions-partition-function)|  |  Splits a sequence of events into multiple partitions based on a condition.   
[`readFile(file, [include], [limit])`](functions-readfile.html "readFile\(\)")| [_`file`_](functions-readfile.html#query-functions-readfile-file)|  |  Uses a `.csv` lookup file or ad-hoc table as data input for the query.   
[`rename([as], field)`](functions-rename.html "rename\(\)")| [_`field`_](functions-rename.html#query-functions-rename-field)|  |  Renames one or more given fields.   
[`replace([as], [field], [flags], regex, [replacement], [with])`](functions-replace.html "replace\(\)")| [_`regex`_](functions-replace.html#query-functions-replace-regex)|  |  Replaces each substring that matches given regular expression with given replacement.   
[`sankey(source, target, [weight])`](functions-sankey.html "sankey\(\)")|  |  |  Produces data compatible with Sankey widget.   
[`series(collect, [endmatch], [maxduration], [maxpause], [memlimit], [separator], [startmatch])`](functions-series.html "series\(\)")| [_`collect`_](functions-series.html#query-functions-series-collect)|  |  Collects a series of values for selected fields from multiple events into one or more events.   
[`setField(target, value)`](functions-setfield.html "setField\(\)")|  |  |  Sets fields whose names are not known but computed from an expression.   
[`slidingTimeWindow([current], function, span, [timestampfield])`](functions-slidingtimewindow.html "slidingTimeWindow\(\)")| [_`function`_](functions-slidingtimewindow.html#query-functions-slidingtimewindow-function)|  |  Applies an aggregation to a moving time-based window of events in a sequence.   
[`slidingWindow([current], events, function)`](functions-slidingwindow.html "slidingWindow\(\)")| [_`function`_](functions-slidingwindow.html#query-functions-slidingwindow-function)|  |  Applies an aggregation to a moving window of a specified number of events in a sequence.   
[`split([field], [strip])`](functions-split.html "split\(\)")| [_`field`_](functions-split.html#query-functions-split-field)|  |  Splits an event structure created by a JSON array into distinct events.   
[`splitString([as], by, [field], [index])`](functions-splitstring.html "splitString\(\)")| [_`field`_](functions-splitstring.html#query-functions-splitstring-field)|  |  Splits a string by specifying a regular expression by which to split.   
[`stripAnsiCodes([as], field)`](functions-stripansicodes.html "stripAnsiCodes\(\)")| [_`field`_](functions-stripansicodes.html#query-functions-stripansicodes-field)|  |  Removes ANSI color codes and movement commands.   
[`text:contains(string, substring)`](functions-text-contains.html "text:contains\(\)")| [_`string`_](functions-text-contains.html#query-functions-text-contains-string)|  |  Tests if a specific substring is present within a given string.   
[`text:endsWith(string, substring)`](functions-text-endswith.html "text:endsWith\(\)")| [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string)|  |  Tests if a specific substring is present at the end of a given string.   
[`text:length([as], string)`](functions-text-length.html "text:length\(\)")| [_`string`_](functions-text-length.html#query-functions-text-length-string)| **added in 1.207**|  Computes the length of a string.   
[`text:positionOf([as], [begin], character, [occurrence], string)`](functions-text-positionof.html "text:positionOf\(\)")| [_`string`_](functions-text-positionof.html#query-functions-text-positionof-string)| **added in 1.207**|  Computes the position of a given character or substring within a string.   
[`text:startsWith(string, substring)`](functions-text-startswith.html "text:startsWith\(\)")| [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string)|  |  Tests if a specific substring is present at the start of a given string.   
[`text:substring([as], [begin], [end], string)`](functions-text-substring.html "text:substring\(\)")| [_`string`_](functions-text-substring.html#query-functions-text-substring-string)| **added in 1.207**|  Extracts a substring from a string given a pair of positions into the string.   
[`transpose([column], [header], [limit], [pivot])`](functions-transpose.html "transpose\(\)")| [_`pivot`_](functions-transpose.html#query-functions-transpose-pivot)|  |  Transposes a query results set by creating an event for each attribute.   
[`unit:convert([as], [binary], field, [from], [keepUnit], [to], [unit])`](functions-unit-convert.html "unit:convert\(\)")| [_`field`_](functions-unit-convert.html#query-functions-unit-convert-field)|  |  Converts values between different units.   
[`upper([as], field, [locale])`](functions-upper.html "upper\(\)")| [_`field`_](functions-upper.html#query-functions-upper-field)|  |  Changes contents of a string field to upper case letters.   
[`urlDecode([as], field)`](functions-urldecode.html "urlDecode\(\)")| [_`field`_](functions-urldecode.html#query-functions-urldecode-field)|  |  URL-decodes the contents of a string field.   
[`urlEncode([as], field, [type])`](functions-urlencode.html "urlEncode\(\)")| [_`field`_](functions-urlencode.html#query-functions-urlencode-field)|  |  URL encodes the contents of a string field.   
[`writeJson([as], [field])`](functions-writejson.html "writeJson\(\)")| [_`field`_](functions-writejson.html#query-functions-writejson-field)|  |  Writes data, including fields, as a JSON object.   
[`xml:prettyPrint([as], field, [step], [strict], [width])`](functions-xml-prettyprint.html "xml:prettyPrint\(\)")| [_`field`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-field)|  |  Nicer output to an XML field.
