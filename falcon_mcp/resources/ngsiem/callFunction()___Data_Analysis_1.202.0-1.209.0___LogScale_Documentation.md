# callFunction() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-callfunction.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`callFunction()`](functions-callfunction.html "callFunction\(\)")

Calls the named function on a field over a set of events. The result is returned in a field named _function for the selected function. This allows having the function name as a dashboard parameter. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-callfunction.html#query-functions-callfunction-as)|  string| optional[a] | `_function`|  Name of output field.   
[_`field`_](functions-callfunction.html#query-functions-callfunction-field)|  string| required |  |  Field to extract a number from and calculate function over.   
[_`function`_](functions-callfunction.html#query-functions-callfunction-function)[b]| string| required |  |  Function to run.   
|  |  | **Values**  
|  |  | [`avg`](functions-callfunction.html#query-functions-callfunction-function-option-avg)| The [`avg()`](functions-avg.html "avg\(\)") function  
|  |  | [`count`](functions-callfunction.html#query-functions-callfunction-function-option-count)| The [`count()`](functions-count.html "count\(\)") function  
|  |  | [`max`](functions-callfunction.html#query-functions-callfunction-function-option-max)| The [`max()`](functions-max.html "max\(\)") function  
|  |  | [`min`](functions-callfunction.html#query-functions-callfunction-function-option-min)| The [`min()`](functions-min.html "min\(\)") function  
|  |  | [`range`](functions-callfunction.html#query-functions-callfunction-function-option-range)| The [`range()`](functions-range.html "range\(\)") function  
|  |  | [`sum`](functions-callfunction.html#query-functions-callfunction-function-option-sum)| The [`sum()`](functions-sum.html "sum\(\)") function  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`function`_](functions-callfunction.html#query-functions-callfunction-function) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`function`_](functions-callfunction.html#query-functions-callfunction-function) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     callFunction("value",field="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     callFunction(function="value",field="value")
> 
> These examples show basic structure only.

### [`callFunction()`](functions-callfunction.html "callFunction\(\)") Examples

Click + next to an example below to get the full details.

#### Call Named Function on a Field - Example 1

**Calls the named function ([`avg()`](functions-avg.html "avg\(\)")) on a field over a set of events **

##### Query

logscale
    
    
    avg_sent:=callFunction("avg", field=bytes_sent)

##### Introduction

In this example, the [`callFunction()`](functions-callfunction.html "callFunction\(\)") function is used to find the average bytes sent in HTTP responses. It calls the named function ([`avg()`](functions-avg.html "avg\(\)")) on a field over a set of events. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         avg_sent:=callFunction("avg", field=bytes_sent)

Finds the average bytes sent in HTTP response, and returns the results in a new field named avg_sent. Notice that the [`avg()`](functions-avg.html "avg\(\)") function is used indirectly in this example. 

  3. Event Result set.




##### Summary and Results

The query is used to find the average bytes sent in HTTP responses. Using a query parameter (for example, `?function`) to select the aggregation function for a [`timeChart()`](functions-timechart.html "timeChart\(\)") is useful for dashboard widgets. 

Using [`callFunction()`](functions-callfunction.html "callFunction\(\)") allow for using a function based on the data or dashboard parameter instead of writing the query directly. 

#### Call Named Function on a Field - Example 2

**Calls the named function ([`count()`](functions-count.html "count\(\)")) on a field over a set of events **

##### Query

logscale
    
    
    timeChart(function=[callFunction(?{function=count}, field=value)])

##### Introduction

In this example, the [`callFunction()`](functions-callfunction.html "callFunction\(\)") function is used to call the named function ([`count()`](functions-count.html "count\(\)")) on a field over a set of events using the query parameter `?function`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timeChart(function=[callFunction(?{function=count}, field=value)])

Counts the events in the value field, and displays the results in a timechart. 

Notice how the query parameter `?function` is used to select the aggregation function for a [`timeChart()`](functions-timechart.html "timeChart\(\)"). 

  3. Event Result set.




##### Summary and Results

The query is used to count events and chart them over time. Because we are using [`callFunction()`](functions-callfunction.html "callFunction\(\)"), it could be a different function based on the dashboard parameter. 

Using a query parameter (for example, `?function`) to select the aggregation function for a [`timeChart()`](functions-timechart.html "timeChart\(\)") is useful for dashboard widgets. 

Using [`callFunction()`](functions-callfunction.html "callFunction\(\)") allow for using a function based on the data or dashboard parameter instead of writing the query directly.
