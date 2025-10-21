# sample() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-sample.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`sample()`](functions-sample.html "sample\(\)")

Samples the event stream. Events that do not have the field being sampled are discarded. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-sample.html#query-functions-sample-field)|  string| optional[a] | `@timestamp`|  The names of the field to use for sampling events.   
[_`percentage`_](functions-sample.html#query-functions-sample-percentage)[b]| double| optional[[a]](functions-sample.html#ftn.table-functions-sample-optparamfn) | [`1`](functions-sample.html#query-functions-sample-percentage-mindefault-1)|  Keep this percentage of the events.   
|  |  | **Values**  
|  |  | [`1`](functions-sample.html#query-functions-sample-percentage-mindefault-1)|   
|  | **Maximum**| [`100`](functions-sample.html#query-functions-sample-percentage-max-100)|   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`percentage`_](functions-sample.html#query-functions-sample-percentage) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`percentage`_](functions-sample.html#query-functions-sample-percentage) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     sample("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     sample(percentage="value")
> 
> These examples show basic structure only.

### [`sample()`](functions-sample.html "sample\(\)") Examples

Click + next to an example below to get the full details.

#### Sample Event Streams - Example 1

**Sample events keeping only specified percentage of the events using the[`sample()`](functions-sample.html "sample\(\)") function **

##### Query

logscale
    
    
    sample(percentage=2)

##### Introduction

Event sampling can be used to determine the characteristics of a large set of data without processing every event. In this example, the [`sample()`](functions-sample.html "sample\(\)") function is used to keep `2%` of the events. If used as part of a query, these randomly selected events are passed to the next stage of the query. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         sample(percentage=2)

Samples events keeping only `2%` of the events. 

  3. Event Result set.




##### Summary and Results

The query is used to sample events keeping only specified percentage of the events. Event sampling can be used to determine the characteristics of a large set of data without processing every event. Sampling is useful in, for example, survey analysis making it possible to draw conclusions without surveying all events. Sampling can also be used to filter on both frequently and infrequently occurring events. 

#### Sample Event Streams - example 2

**Sample events keeping only specified percentage of the events and sort by host using the[`sample()`](functions-sample.html "sample\(\)") function with [`groupBy()`](functions-groupby.html "groupBy\(\)") and [`sort()`](functions-sort.html "sort\(\)") **

##### Query

logscale
    
    
    sample(percentage=0.1)
    | groupBy(host)
    | sort()

##### Introduction

Event sampling can be used to determine the characteristics of a large set of data without processing every event. In this example, the [`sample()`](functions-sample.html "sample\(\)") function is used to keep `0.1%` of the events and find the most common hosts among the sampled events. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         sample(percentage=0.1)

Samples events keeping only `0.1%` of the events. These randomly selected events are passed to the next stage of the query. 

  3. logscale
         
         | groupBy(host)

Groups the sampled events by the host field. 

The advantage of sampling events before grouping them is, that it allows for analysis of common patterns without hitting [`groupBy()`](functions-groupby.html "groupBy\(\)") limits. 

  4. logscale
         
         | sort()

Sorts the returned results by their host to find the most common host (by default, in descending order of count). 

  5. Event Result set.




##### Summary and Results

The query is used to sample events keeping only specified percentage of the events, and then find the most common host among the sampled events. Event sampling can be used to determine the characteristics of a large set of data without processing every event. Sampling is useful in for example survey analysis making it possible to draw conclusions without surveying all events. Sampling can also be used to filter on both frequently and infrequently occurring events.
