# array:sort() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-sort.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:sort()`](functions-array-sort.html "array:sort\(\)")

This function sorts the elements of an array of values using the given sorting data type and order. 

By default, this function replaces the input array with the sorted result, but it is possible to specify a different output array using a parameter. 

The elements can be sorted as strings (lexicographically) or as numbers, either ascending and descending. Default is ascending. 

Sorting as strings is case insensitive and elements that are identical except for case are kept in unspecified order. When sorting as numbers, elements that are not numbers, are sorted separately as strings, and appear after the numbers in the output array (regardless of sort order). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-sort.html#query-functions-array-sort-array)[a]| array name| required |  |  The array to sort elements in. Must follow valid [Array Syntax](syntax-array.html "Array Syntax"). For example, for an array of fields incidents[0], incidents[1], and so on, this would be incidents[].   
[_`asArray`_](functions-array-sort.html#query-functions-array-sort-asarray)|  string| optional[b] | `input array`|  Where to output the sorted array. The output array is not explicitly terminated, that is, if an array already exists, parts of it or the whole array may be overwritten.   
[_`order`_](functions-array-sort.html#query-functions-array-sort-order)|  string| optional[[b]](functions-array-sort.html#ftn.table-functions-array-sort-optparamfn) | `asc`|  The order in which to sort. The short variants `asc` and `desc` can also be used.   
|  |  | **Values**  
|  |  | [`ascending`](functions-array-sort.html#query-functions-array-sort-order-option-ascending)| Sort ascending  
|  |  | [`descending`](functions-array-sort.html#query-functions-array-sort-order-option-descending)| Sort descending  
[ _`type`_](functions-array-sort.html#query-functions-array-sort-type)|  string| optional[[b]](functions-array-sort.html#ftn.table-functions-array-sort-optparamfn) | [`string`](functions-array-sort.html#query-functions-array-sort-type-option-string)|  The type of data to sort by.   
|  |  | **Values**  
|  |  | [`number`](functions-array-sort.html#query-functions-array-sort-type-option-number)| Treat the field as numerical and sort in numerical order  
|  |  | [`string`](functions-array-sort.html#query-functions-array-sort-type-option-string)| Treat the field as string values and sort alphabetical  
[a] The parameter name [_`array`_](functions-array-sort.html#query-functions-array-sort-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-sort.html#query-functions-array-sort-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:sort("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:sort(array="value")
> 
> These examples show basic structure only.

### [`array:sort()`](functions-array-sort.html "array:sort\(\)") Function Operation

The [`array:sort()`](functions-array-sort.html "array:sort\(\)") function has specific implementation and operational considerations, outlined below. 

  * Like other array functions, [`array:sort()`](functions-array-sort.html "array:sort\(\)") overwrites the elements of the target array, if the array already exists. If the target array has more entries than the source array, the [`array:sort()`](functions-array-sort.html "array:sort\(\)") does not remove additional entries in the target array. 

  * A specific syntax applies for this query function, see [Array Syntax](syntax-array.html "Array Syntax") for details. 




### [`array:sort()`](functions-array-sort.html "array:sort\(\)") Syntax Examples

In the following are examples of usage: 

By default, the elements of the array are sorted as strings in ascending order. Sorting as strings is case insensitive. 

Raw Events

{ \"array\": [\"date\", \"apple\", \"Coconut\", \"Cherry\", \"coconut\", \"banana\"]}"]  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("array[]")

Sample output from the incoming example data: 

array[0]| array[1]| array[2]| array[3]| array[4]| array[5]  
---|---|---|---|---|---  
apple| banana| Cherry| Coconut| coconut| date  
  
When sorting as strings, numbers are treated as strings and sorted digit by digit. 

Raw Events

{\"array\": [5, 2, 11, 2, 10, 41]}"])  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("array[]")

Sample output from the incoming example data: 

array[0]| array[1]| array[2]| array[3]| array[4]| array[5]  
---|---|---|---|---|---  
10| 11| 2| 2| 41| 5  
  
To sort numbers by value, the type has to be specified as number. 

Raw Events

{\"array\": [5, 2, 11, 2, 10, 41]}"])  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("array[]", type=number)

Sample output from the incoming example data: 

array[0]| array[1]| array[2]| array[3]| array[4]| array[5]  
---|---|---|---|---|---  
2| 2| 5| 10| 11| 41  
  
The sorted elements can be written to a different array using the _`asArray`_ parameter. 

Raw Events

{ \"array\": [\"date\", \"apple\", \"Coconut\", \"Cherry\", \"coconut\", \"banana\"]}  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("array[]", asArray="sorted[]")

Sample output from the incoming example data: 

array[0]| array[1]| array[2]| array[3]| array[4]| array[5]| sorted[0]| sorted[1]| sorted[2]| sorted[3]| sorted[4]| sorted[5]  
---|---|---|---|---|---|---|---|---|---|---|---  
date| apple| Coconut| Cherry| coconut| banana| apple| banana| Cherry| Coconut| coconut| date  
  
The order of the result can be specified using the [_`order`_](functions-array-sort.html#query-functions-array-sort-order) parameter. Default is ascending. 

Raw Events

{\"array\": [5, 2, 11, 2, 10, 41]}"])  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("array[]", type=number, order=descending)

Sample output from the incoming example data: 

array[0]| array[1]| array[2]| array[3]| array[4]| array[5]  
---|---|---|---|---|---  
41| 11| 10| 5| 2| 2  
  
When sorting as numbers, the elements that are not numbers, are sorted separately and appear after the sorted numbers. 

Raw Events

{\"array\": [\"banana\", 5, 2, \"apple\", 10, 41]}"])  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("array[]", type=number)

Sample output from the incoming example data: 

array[0]| array[1]| array[2]| array[3]| array[4]| array[5]  
---|---|---|---|---|---  
2| 5| 10| 41| apple| banana  
  
This is also the case for descending number sorting. 

Raw Events

{\"array\": [\"banana\", 5, 2, \"apple\", 10, 41]}"])  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("array[]", type=number, order=descending)

Sample output from the incoming example data: 

array[0]| array[1]| array[2]| array[3]| array[4]| array[5]  
---|---|---|---|---|---  
41| 10| 5| 2| banana| apple  
  
Overwriting the entries of the target array if it already exists, but if the target array has more entries than the source array, the additional entries of the target array are not removed. 

Raw Events

{\"a\": [3, 1, 2], \"b\": [5, 5, 5, 5]}"])  
---  
  
Specify the name of the array field from which to sort: 

logscale
    
    
    parseJson()
    | array:sort("a[]", asArray="b[]")

Sample output from the incoming example data: 

a[0]| a[1]| a[2]| b[0]| b[1]| b[2]| b[3]  
---|---|---|---|---|---|---  
3| 1| 2| 1| 2| 3| 5
