# array:reduceRow() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-reducerow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:reduceRow()`](functions-array-reducerow.html "array:reduceRow\(\)")

### Important

This function is considered experimental and under active development and should not be used in production. 

The function must be enabled using the feature flag ArrayFunctions. See [Enabling & Disabling Feature Flags](https://library.humio.com/deployment/configuration-enabling-features.html). 

Computes an aggregated value of an array on all events. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-reducerow.html#query-functions-array-reducerow-array)[a]| string| required |  |  The prefix of the array in LogScale, for example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents`.   
[_`as`_](functions-array-reducerow.html#query-functions-array-reducerow-as)|  string| optional[b] | `_reduceRow`|  Name of the output array.   
[_`function`_](functions-array-reducerow.html#query-functions-array-reducerow-function)|  function| required |  |  Aggregate function to use (for example, [`max()`](functions-max.html "max\(\)")). Must be an aggregate function that outputs a single event with a single field.   
[_`var`_](functions-array-reducerow.html#query-functions-array-reducerow-var)|  string| required |  |  Placeholder field name to use for array element to use in aggregate function.   
[a] The parameter name [_`array`_](functions-array-reducerow.html#query-functions-array-reducerow-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-reducerow.html#query-functions-array-reducerow-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:reduceRow("value",var="value",function="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:reduceRow(array="value",var="value",function="value")
> 
> These examples show basic structure only.

Only aggregate functions that return a single event with a single field (such as [`avg()`](functions-avg.html "avg\(\)"), [`count()`](functions-count.html "count\(\)"), [`sum()`](functions-sum.html "sum\(\)"), [`max()`](functions-max.html "max\(\)") etc.) are allowed as the [_`function`_](functions-array-reducerow.html#query-functions-array-reducerow-function) argument. 

The function cannot be [`join()`](functions-join.html "join\(\)") or [`groupBy()`](functions-groupby.html "groupBy\(\)"). 

### [`array:reduceRow()`](functions-array-reducerow.html "array:reduceRow\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Average of Field Values in an Array

**Calculate Average of Field Values in a flat array using the[`array:reduceRow()`](functions-array-reducerow.html "array:reduceRow\(\)") function **

##### Query

logscale
    
    
    array:reduceRow("ages[]", var=x, function=avg(x))

##### Introduction

In this example, the [`array:reduceRow()`](functions-array-reducerow.html "array:reduceRow\(\)") function is used to calculate the average age of the field ages and return the result in a field named _reduceRow._avg. 

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
         
         array:reduceRow("ages[]", var=x, function=avg(x))

Produces two events, calculating the average value across the ages[] array for each event. The results are placed into the _avg field for each new event. 

  3. Event Result set.




##### Summary and Results

The query is used to calculate averages for a given array for each event and is a shorthand version of using [`array:eval()`](functions-array-eval.html "array:eval\(\)") specifically for processing each event. 

Sample output from the incoming example data: 

ages[0]| ages[1]| ages[2]| _avg  
---|---|---|---  
16| 32| 64| 37.333  
15| 30| 45| 30  
1| 2| 4| 2.67  
89| 57| 67| 71  
  
Note that the evaluation is per event, for example per row of the overall table of values across the array over all events. To calculate values across the column of values, use [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)").
