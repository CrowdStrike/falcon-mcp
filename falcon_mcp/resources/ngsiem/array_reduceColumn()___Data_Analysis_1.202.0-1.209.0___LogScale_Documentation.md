# array:reduceColumn() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-reducecolumn.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)")

### Important

This function is considered experimental and under active development and should not be used in production. 

The function must be enabled using the feature flag ArrayFunctions. See [Enabling & Disabling Feature Flags](https://library.humio.com/deployment/configuration-enabling-features.html). 

Computes an aggregate value for each array element with the same index. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-array)[a]| string| required |  |  The prefix of the array in LogScale, for example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents`.   
[_`as`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-as)|  string| optional[b] | `_reduceColumn`|  Name of the output array.   
[_`function`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-function)|  array of aggregate functions| required |  |  Aggregate function to use (for example, [`max()`](functions-max.html "max\(\)")). If several aggregators are listed for the [_`function`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-function) parameter, then their outputs are combined using the rules described for [`stats()`](functions-stats.html "stats\(\)").   
[_`var`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-var)|  string| required |  |  Placeholder field name to use for array elements in the aggregate function.   
[a] The parameter name [_`array`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:reduceColumn("value",var="value",function="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:reduceColumn(array="value",var="value",function="value")
> 
> These examples show basic structure only.

If, for example, all events contain arrays with the time taken for 3 different tasks, the query 

logscale
    
    
    array:reduceColumn(times, var=x,function=[avg(x), max(x)])

will compute the maximum and average time for each task. 

If [_`function`_](functions-array-reducecolumn.html#query-functions-array-reducecolumn-function) is an aggregator that produces more than one event, such as [`groupBy()`](functions-groupby.html "groupBy\(\)"), the output of [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") will contain the same number of events as the maximum number of events produced in a column. The nth event will contain an array with the values from the nth event in all columns having an nth event. This can lead to unreliable ordering of the output if the internal aggregate does not output ordered events (such as [`groupBy()`](functions-groupby.html "groupBy\(\)")). 

### [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") Examples

Click + next to an example below to get the full details.

#### Compute Aggregate Value for Each Array Element With Same Index

**Compute an aggregate value for each array element with the same index using the[`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") **

##### Query

logscale
    
    
    maxTimes := array:reduceColumn(times, var=x, function={time := max(x)})

##### Introduction

In this example, the [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") function is used to find the maximum time for each array element with same index in a flat array. 

Example incoming data might look like this: 

times[0]| times[1]| times[2]  
---|---|---  
1| 2| 3  
5| 1| 0  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         maxTimes := array:reduceColumn(times, var=x, function={time := max(x)})

Computes the maximum time for each array element with same index in the array and reduces it to one value. 

  3. Event Result set.




##### Summary and Results

The query is used to find the maximum time for each array element with same index in a flat array. 

_reduceColumn[0]| _reduceColumn[1]| _reduceColumn[2]  
---|---|---  
5| 2| 3  
  
#### Compute Average Value for Each Array Element With Same Index

**Compute an average value for each array element with the same index across multiple events using the[`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") **

##### Query

logscale
    
    
    maxTimes := array:reduceColumn("ages[]", var=x, function=avg(x))

##### Introduction

In this example, the [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") function is used to find the maximum time for each array element with same index in a flat array. 

Example incoming data might look like this: 

ages[0]| ages[1]| ages[2]  
---|---|---  
16| 32| 64  
15| 30| 45  
1| 2| 4  
89| 57| 67  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         maxTimes := array:reduceColumn("ages[]", var=x, function=avg(x))

Computes the average for each array element with same index in the array and reduces it to one value, placing the result for each index into a new field _reduceColumn. 

  3. Event Result set.




##### Summary and Results

The query is used to find the maximum time for each array element with same index in a flat array. 

_reduceColumn[0]| _reduceColumn[1]| _reduceColumn[2]| _reduceColumn[3]  
---|---|---|---  
40.3| 40.3| 63.3|
