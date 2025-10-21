# duration() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-duration.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`duration()`](functions-duration.html "duration\(\)")

This function computes the number of milliseconds in a certain fixed time period. It is used to make timestamp comparisons easier, more readable and less error-prone. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-duration.html#query-functions-duration-as)|  string| optional[a] | `_duration`|  The name of the output field.   
[_`duration`_](functions-duration.html#query-functions-duration-duration)[b]| string| required |  |  The time duration specification. It is defined as a [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax") such as `5m` or `2d`.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`duration`_](functions-duration.html#query-functions-duration-duration) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`duration`_](functions-duration.html#query-functions-duration-duration) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     duration("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     duration(duration="value")
> 
> These examples show basic structure only.

The field selected by the [_`as`_](functions-duration.html#query-functions-duration-as) argument returns the number of milliseconds in the duration specified by the [_`duration`_](functions-duration.html#query-functions-duration-duration) argument. The [_`duration`_](functions-duration.html#query-functions-duration-duration) argument follows the same syntax and semantics as the duration specification mini-language used elsewhere in the system. For more information on time duration, see [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax"). 

Important

### Anchored time units not supported

You cannot use [Calendar-Based Units](syntax-time-relative.html#syntax-time-relative-advanced-calendar "Calendar-Based Units") and [Anchoring to Specific Time Units](syntax-time-relative.html#syntax-time-relative-advanced-anchor "Anchoring to Specific Time Units") to define the span length in the [`duration()`](functions-duration.html "duration\(\)") function. 

### [`duration()`](functions-duration.html "duration\(\)") Examples

Click + next to an example below to get the full details.

#### Compare Two Timestamps

****

##### Query

logscale
    
    
    diff := endTime - startTime
    | test(diff > duration("5m"))

##### Introduction

In this example, the [`duration()`](functions-duration.html "duration\(\)") function is used to compute a simple value to use in a comparison. The input data contains the startTime and endTime for an operation, to determine whether the difference between the two exceeds a duration of 5 minutes. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         diff := endTime - startTime

Determines the difference between the endTime and startTime; the fields should be in milliseconds (as they would be for an epoch or timestamp). 

  3. logscale
         
         | test(diff > duration("5m"))

Use the [`test()`](functions-test.html "test\(\)") function to determine if the computed difference is greater than a duration of 5 minutes. In this case, [`duration()`](functions-duration.html "duration\(\)") returns 300,000. 

  4. Event Result set.




##### Summary and Results

The [`duration()`](functions-duration.html "duration\(\)") functions supports a more convenient, and human-readable, method of defining a duration without needing to explicitly calculate the comparison. This is particularly useful when using parameters on a dashboard. 

#### Narrow the Search Interval

****

##### Query

logscale
    
    
    test(@timestamp > now() - duration("2d"))

##### Introduction

When searching across a range of timestamps, the ability to limit the search to a more specific range using a relative duration can limit the output. To achieve this with the search, make use of [`duration()`](functions-duration.html "duration\(\)") with a relative time, for example `2d` for two days and use this to compare against the current time and @timestamp of the event. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(@timestamp > now() - duration("2d"))

Creates a value based on a duration of `2d` (two days). This returns a value in milliseconds (`2 * 24 * 60 * 60 * 1000`). By subtracting the value from [`now()`](functions-now.html "now\(\)") the value is two days ago from the time the event is executed. Then the value is compared to the @timestamp to filter the events. 

  3. Event Result set.




##### Summary and Results

The result is syntactically equivalent to: 

logscale
    
    
    test(@timestamp > now() - 172800000)

As the value is in a human-readable and relative time syntax, the value can be used in dashboards and user-selected parameters.
