# Array Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Array Query Functions

LogScale's array functions allow you to extract, create and manipulate items embedded in arrays, or to interpret arrays and nested arrays within events. In the [Array Query Functions](functions-array.html#table_functions-array "Table: Array Query Functions") table, functions marked with `array` can be used with a flat array. Functions marked `nested-array` are designed for working with structured arrays. 

Arrays can be parsed from incoming events using the [`splitString()`](functions-splitstring.html "splitString\(\)") or [`parseJson()`](functions-parsejson.html "parseJson\(\)") functions. 

For information on using arrays, see [Array Syntax](syntax-array.html "Array Syntax"). 

**Table: Array Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`array:append(array, values)`](functions-array-append.html "array:append\(\)")| [_`array`_](functions-array-append.html#query-functions-array-append-array)|  |  Appends single or multiple values to an array, or creates a new array if it does not already exist.   
[`array:contains(array, value)`](functions-array-contains.html "array:contains\(\)")| [_`array`_](functions-array-contains.html#query-functions-array-contains-array)|  |  Checks whether the given value matches any of the values of the array and excludes the event if no value matches.   
[`array:dedup(array, [asArray])`](functions-array-dedup.html "array:dedup\(\)")| [_`array`_](functions-array-dedup.html#query-functions-array-dedup-array)|  |  [`array:dedup()`](functions-array-dedup.html "array:dedup\(\)") removes duplicate elements from an array. The ordering of the first occurrence of each unique element is preserved.   
[`array:drop(array)`](functions-array-drop.html "array:drop\(\)")| [_`array`_](functions-array-drop.html#query-functions-array-drop-array)|  |  Takes the name of an array and drops all fields of this array.   
[`array:eval(array, [asArray], function, [var])`](functions-array-eval.html "array:eval\(\)")| [_`array`_](functions-array-eval.html#query-functions-array-eval-array)|  |  Evaluates the function argument on all values in the array under the array argument overwriting the array.   
[`array:exists(array, condition, [var])`](functions-array-exists.html "array:exists\(\)")| [_`array`_](functions-array-exists.html#query-functions-array-exists-array)|  |  Filters events based on whether the given array contains an element that satisfies a given condition (based on the array argument). Recommended for flat arrays. Does not work on nested arrays — use [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") instead.   
[`array:filter(array, [asArray], function, [var])`](functions-array-filter.html "array:filter\(\)")| [_`array`_](functions-array-filter.html#query-functions-array-filter-array)|  |  Drops entries from the input array using the given filtering function.   
[`array:intersection(array, [as])`](functions-array-intersection.html "array:intersection\(\)")| [_`array`_](functions-array-intersection.html#query-functions-array-intersection-array)|  |  Determines the set intersection of array values over input events.   
[`array:length(array, [as])`](functions-array-length.html "array:length\(\)")| [_`array`_](functions-array-length.html#query-functions-array-length-array)|  |  Counts the number of elements in an array.   
[`array:reduceAll(array, function, var)`](functions-array-reduceall.html "array:reduceAll\(\)")| [_`array`_](functions-array-reduceall.html#query-functions-array-reduceall-array)|  |  Computes a value from all events and array elements of the specified array.   
[`array:reduceColumn(array, [as], function, var)`](functions-array-reducecolumn.html "array:reduceColumn\(\)")| [_`array`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-array)|  |  Computes an aggregate value for each array element with the same index.   
[`array:reduceRow(array, [as], function, var)`](functions-array-reducerow.html "array:reduceRow\(\)")| [_`array`_](functions-array-reducerow.html#query-functions-array-reducerow-array)|  |  Computes an aggregated value of an array on all events.   
[`array:regex(array, [flags], regex)`](functions-array-regex.html "array:regex\(\)")| [_`array`_](functions-array-regex.html#query-functions-array-regex-array)|  |  Checks whether the given pattern matches any of the values of the array and excludes the event from the search result.   
[`array:rename(array, asArray)`](functions-array-rename.html "array:rename\(\)")| [_`array`_](functions-array-rename.html#query-functions-array-rename-array)|  |  Takes the name of an array and renames all fields of this array.   
[`array:sort(array, [asArray], [order], [type])`](functions-array-sort.html "array:sort\(\)")| [_`array`_](functions-array-sort.html#query-functions-array-sort-array)|  |  Sorts the elements of an array of values using the given sorting data type and order.   
[`array:union(array, [as])`](functions-array-union.html "array:union\(\)")| [_`array`_](functions-array-union.html#query-functions-array-union-array)|  |  Determines the set union of array values over input events.   
[`concatArray([as], field, [from], [prefix], [separator], [suffix], [to])`](functions-concatarray.html "concatArray\(\)")| [_`field`_](functions-concatarray.html#query-functions-concatarray-field)|  |  Concatenates values of all fields with same name and an array suffix into a new field.   
[`objectArray:eval(array, asArray, function, [var])`](functions-objectarray-eval.html "objectArray:eval\(\)")| [_`array`_](functions-objectarray-eval.html#query-functions-objectarray-eval-array)|  |  Maps over an array of objects and outputs a new array of the mapped values.   
[`objectArray:exists(array, condition, [var])`](functions-objectarray-exists.html "objectArray:exists\(\)")| [_`array`_](functions-objectarray-exists.html#query-functions-objectarray-exists-array)|  |  Filters events based on whether the given array contains an element that satisfies a given condition (based on the array argument). Recommended for nested arrays.   
[`split([field], [strip])`](functions-split.html "split\(\)")| [_`field`_](functions-split.html#query-functions-split-field)|  |  Splits an event structure created by a JSON array into distinct events.   
[`splitString([as], by, [field], [index])`](functions-splitstring.html "splitString\(\)")| [_`field`_](functions-splitstring.html#query-functions-splitstring-field)|  |  Splits a string by specifying a regular expression by which to split.   
  
  


### Using Array Query Functions

The following rules and recommendations apply to all the array query functions listed in the [Array Query Functions](functions-array.html#table_functions-array "Table: Array Query Functions") table. 

  * Array functions do not support non-consecutive items in an array. 

For example, when manipulating the array: 

logscale Syntax
        
        foo[0], foo[1], foo[3]

The function will only run against: 

logscale Syntax
        
        foo[0], foo[1]

  * Array indexes start at zero; For example, foo[0]. 

  * When referring to the whole array, use foo[]. 

  * Arrays elements are identified using the array name with an [x] suffix. 

For example, having the array: 

logscale Syntax
        
        foo[0], foo[1]

Adding another field: 

logscale Syntax
        
        foo[2]

Results in the array: 

logscale Syntax
        
        foo[0],foo[1],foo[2]

With no missing entries, array functions will run against them all. 

  * Field names that have special characters (such as colons) or spaces need to be enclosed in backtick quotes to be properly identified in array functions: 

logscale
        
        array:contains("log:errorcode[]", value=3)

If quotes are missing, those fields are not recognized as valid array arguments and an error message is shown in the Query Editor.
