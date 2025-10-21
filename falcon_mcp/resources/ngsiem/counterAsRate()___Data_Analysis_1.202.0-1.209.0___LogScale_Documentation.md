# counterAsRate() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-counterasrate.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`counterAsRate()`](functions-counterasrate.html "counterAsRate\(\)")

Calculates the rate for a counter field. This function can show the rate at which a counter changes. The result is returned in a field named _rate with the unit being events/second. 

[`counterAsRate()`](functions-counterasrate.html "counterAsRate\(\)") is often expected to be used as the function parameter in a [`timeChart()`](functions-timechart.html "timeChart\(\)") or [`groupBy()`](functions-groupby.html "groupBy\(\)") function. 

### Important

This function requires at least two points for calculating a rate. When used in a [`Time Chart`](widgets-timechart.html "Time Chart") , it is important to have at least two points in each bucket. 

This function expects the field to have monotonic increasing values over time. If this is not the case no result is returned. Counters are often reset at server restarts or deployments. Running rate over a reset would not return a result. Using [`counterAsRate()`](functions-counterasrate.html "counterAsRate\(\)") in a [`timeChart()`](functions-timechart.html "timeChart\(\)") returns a rate for each bucket where the counter was not reset and nothing for the buckets where the counter was reset. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-counterasrate.html#query-functions-counterasrate-as)|  string| optional[a] | `_rate`|  Name of output field.   
[_`field`_](functions-counterasrate.html#query-functions-counterasrate-field)[b]| string| required |  |  Field from which to extract a number and over which to calculate rate.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-counterasrate.html#query-functions-counterasrate-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-counterasrate.html#query-functions-counterasrate-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     counterAsRate("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     counterAsRate(field="value")
> 
> These examples show basic structure only.

### [`counterAsRate()`](functions-counterasrate.html "counterAsRate\(\)") Syntax Examples

Show the rate of a counter over time: 

logscale
    
    
    timeChart(function=counterAsRate(counter))

Show the rate of a counter with one series for each host over time, displaying the rate as events per minute: 

logscale
    
    
    timeChart(host, function=counterAsRate(counter), unit="1/sec to 1/min")
