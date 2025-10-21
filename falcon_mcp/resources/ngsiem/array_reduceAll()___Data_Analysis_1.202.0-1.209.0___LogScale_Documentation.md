# array:reduceAll() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-reduceall.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:reduceAll()`](functions-array-reduceall.html "array:reduceAll\(\)")

Computes a value from all events and array elements of the specified array. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-reduceall.html#query-functions-array-reduceall-array)[a]| string| required |  |  A string in the format of a valid array followed by `[]`. A valid array can either be an identifier, a valid array followed by `.` and an identifier, or a valid array followed by an array index surrounded by square brackets. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`.   
[_`function`_](functions-array-reduceall.html#query-functions-array-reduceall-function)|  array of aggregate functions| required |  |  The function to be applied to each element. If several aggregators are listed for the [_`function`_](functions-array-reduceall.html#query-functions-array-reduceall-function) parameter, then their outputs are combined using the rules described for [`stats()`](functions-stats.html "stats\(\)").   
[_`var`_](functions-array-reduceall.html#query-functions-array-reduceall-var)|  string| required |  |  Array element field name to use in the function.   
[a] The parameter name [_`array`_](functions-array-reduceall.html#query-functions-array-reduceall-array) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-reduceall.html#query-functions-array-reduceall-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:reduceAll("value",var="value",function="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:reduceAll(array="value",var="value",function="value")
> 
> These examples show basic structure only.

### [`array:reduceAll()`](functions-array-reduceall.html "array:reduceAll\(\)") Function Operation

Syntactically, the function is similar to: 

logscale Syntax
    
    
    split(array)
    | function(array)

but is more efficient. 

The function applies to all the values across multiple events. 

For example, with three events each containing an array `a[]` such that: 

a[0]| a[1]| a[2]  
---|---|---  
1| 4| 2  
3| 5| 2  
5| 2| 3  
  
Where the rows of `a[]` across all events are: 

logscale Syntax
    
    
    [1, 4, 2]
    [3, 5, 2]
    [5, 2, 3]

Running: 

logscale
    
    
    array:reduceAll("a[]", function=avg(x), var=x)

would result in the output: 

logscale
    
    
    _avg=3

since `x` would take the values of: 

logscale Syntax
    
    
    {1, 4, 2, 3, 5, 2, 5, 2, 3}

### [`array:reduceAll()`](functions-array-reduceall.html "array:reduceAll\(\)") Examples

Click + next to an example below to get the full details.

#### Compute an Aggregated Value of an Array on All Events

**Compute an aggregated value of a flat array on all events using the[`array:reduceAll()`](functions-array-reduceall.html "array:reduceAll\(\)") function **

##### Query

logscale
    
    
    array:reduceAll("values[]", var=x, function=max(x))

##### Introduction

In this example, the aggregate function [`max()`](functions-max.html "max\(\)") is used to output a single event with a single field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:reduceAll("values[]", var=x, function=max(x))

Computes the maximum value over all the values within the array values[] by using the [`max()`](functions-max.html "max\(\)") on each element, and then across each event in the event set. 

  3. Event Result set.




##### Summary and Results

The query is used to compute a value from all events and array elements of a specified array. The `reduce()` method is recommended, when you need to have a single value returned from iterating over your array. Only aggregate functions that return a single event with a single field (such as [`avg()`](functions-avg.html "avg\(\)"), [`count()`](functions-count.html "count\(\)"), [`sum()`](functions-sum.html "sum\(\)"), [`max()`](functions-max.html "max\(\)") etc.) are allowed as the [_`function`_](functions-array-reduceall.html#query-functions-array-reduceall-function) argument.
