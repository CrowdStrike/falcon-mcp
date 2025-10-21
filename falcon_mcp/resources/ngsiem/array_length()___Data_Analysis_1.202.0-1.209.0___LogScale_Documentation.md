# array:length() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-length.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:length()`](functions-array-length.html "array:length\(\)")

Provides the number of elements in an array. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-length.html#query-functions-array-length-array)[a]| string| required |  |  Name of the array. For example, `incidents[]`.   
[_`as`_](functions-array-length.html#query-functions-array-length-as)|  string| optional[b] | `_length`|  Name of field that contains the output length.   
[a] The parameter name [_`array`_](functions-array-length.html#query-functions-array-length-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-length.html#query-functions-array-length-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:length("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:length(array="value")
> 
> These examples show basic structure only.

### [`array:length()`](functions-array-length.html "array:length\(\)") Syntax Examples

Given an event with an array field like animals[]: 

animals[0]| animals[1]| animals[2]  
---|---|---  
horse| duck| bunny  
  
and the following query: 

logscale
    
    
    array:length("animals[]")

The result is the number of elements found in the animals[] array field (`horse`, `duck` and `bunny` ) for that event: 

_length  
---  
3  
  
Only array elements in sequential order are counted — if there is a gap in the array, the function assumes it is the end of the array. 

For example, given the event: 

animals[0]| animals[1]| animals[3]  
---|---|---  
horse| duck| bunny  
  
The query counts the first two elements only, thus it will output: 
    
    
    _length: 2

If applied to non-array input fields, the function returns `0`. 

Event: 

Raw Events

#kind: logs  
---  
  
Query: 

logscale Syntax
    
    
    array:length("#kind")

Output: 
    
    
    _length: 0

### [`array:length()`](functions-array-length.html "array:length\(\)") Examples

Click + next to an example below to get the full details.

#### Count Array Elements - Example 1

****

##### Query

logscale
    
    
    array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

##### Introduction

Given an event that has multiple queryParserMetrics.function[] array fields (a list of the functions used in a query): 

queryParserMetrics.function[0]="head"  
---  
queryParserMetrics.function[1]="bucket"  
queryParserMetrics.functions[2]="groupBy"  
  
We want to get the number of functions listed in the `queryParserMetrics.function[]` arrays for that event. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

Counts the elements (the functions in the array) in the `queryParserMetrics.function[]` array field. 

  3. Event Result set.




##### Summary and Results

The returned value is the number of functions found in the array, and it will be output into the _numberOfFunctions field, which is set by the argument [_`as`_](functions-array-length.html#query-functions-array-length-as). 

_numberOfFunctions| 3  
---|---  
  
#### Count Array Elements - Example 2

****

##### Query

logscale
    
    
    queryParserMetrics.function[0] = "head"
    | array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

##### Introduction

Given an event that has the queryParserMetrics.function[] array fields (a list of the functions used in a query): 

queryParserMetrics.function[0]="head"  
---  
queryParserMetrics.function[1]="bucket"  
queryParserMetrics.functions[2]="groupBy"  
  
Filters only events that has `head` as the value of queryParserMetrics.function[] array field, and then gets the number of functions listed in the `queryParserMetrics.function[]` array for that event. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         queryParserMetrics.function[0] = "head"

Filters events that has `head` as the value of queryParserMetrics.function[0] array field. 

  3. logscale
         
         | array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

Counts the elements (the functions used) in all the `queryParserMetrics.function[]` arrays for that event. 

  4. Event Result set.




##### Summary and Results

You will get an array of all the functions used in just one event where `head` is the first function used. The result will be output into the _numberOfFunctions field set by the argument [_`as`_](functions-array-length.html#query-functions-array-length-as). 

_numberOfFunctions| 1  
---|---
