# collect() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-collect.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`collect()`](functions-collect.html "collect\(\)")

Collects a set of values from one or more fields. The [`collect()`](functions-collect.html "collect\(\)") function outputs these values in two possible formats: either as a single concatenated string, or as multiple rows with individual values. 

The sequence of output values is undefined and does not follow any specific order. 

The [`collect()`](functions-collect.html "collect\(\)") function operates under two collection restrictions: A maximum number of values and a maximum memory allocation. 

The [_`limit`_](functions-collect.html#query-functions-collect-limit) parameter defines the maximum number of values that can be collected. 

The memory limit depends on where the function is used: 10 MiB if [`collect()`](functions-collect.html "collect\(\)") is run as a top level function and 1 MiB for all other contexts. 

When the [`collect()`](functions-collect.html "collect\(\)") function exceeds either limitation, it returns partial results and displays a warning message that explains the situation. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`fields`_](functions-collect.html#query-functions-collect-fields)[a]| array of strings| required |  |  Names of the fields to collect values for.   
[_`limit`_](functions-collect.html#query-functions-collect-limit)|  integer| optional[b] | `2000`|  Limit to number of distinct values to collect.   
|  | **Minimum**| `1`|   
[ _`multival`_](functions-collect.html#query-functions-collect-multival)|  boolean| optional[[b]](functions-collect.html#ftn.table-functions-collect-optparamfn) | [`true`](functions-collect.html#query-functions-collect-multival-option-true)|  Whether to output values as a concatenation.   
|  |  | **Values**  
|  |  | [`false`](functions-collect.html#query-functions-collect-multival-option-false)| Output as multiple rows containing individual values  
|  |  | [`true`](functions-collect.html#query-functions-collect-multival-option-true)| Output as a single concatenated string  
[ _`separator`_](functions-collect.html#query-functions-collect-separator)|  string| optional[[b]](functions-collect.html#ftn.table-functions-collect-optparamfn) | `\n`|  Separator used when concatenating values (when [_`multival=true`_](functions-collect.html#query-functions-collect-multival)).   
[a] The parameter name [_`fields`_](functions-collect.html#query-functions-collect-fields) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`fields`_](functions-collect.html#query-functions-collect-fields) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     collect(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     collect(fields=["value"])
> 
> These examples show basic structure only.

### [`collect()`](functions-collect.html "collect\(\)") Function Operation

The [`collect()`](functions-collect.html "collect\(\)") function is limited in the memory for while collecting data before the data is aggregated. The limit changes depending on whether [`collect()`](functions-collect.html "collect\(\)") runs as a top level function — in which case its limit is 10 MiB: 

logscale
    
    
    #type = humio #kind=logs
    | collect(myField)

or whether it runs in a subquery, or as a sub-aggregator to another function — in which case its limit is 1 MiB: 

logscale
    
    
    #type=humio #kind=logs
    groupBy(myField, function=collect(myOtherField))

### Warning

Collecting the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field currently only works when a single timestamp exists. You can work around this restriction by renaming or making another field and collecting that instead, for example: 

logscale
    
    
    timestamp := @timestamp
    | collect(timestamp)

If you do not need more than a single value, consider using the [`selectLast()`](functions-selectlast.html "selectLast\(\)") function or setting `limit=1`, if you experience that the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field not having a value. 

### [`collect()`](functions-collect.html "collect\(\)") Examples

Click + next to an example below to get the full details.

#### Collect and Group Events by Specified Field - Example 1

**Collect and group events by specified field using[`collect()`](functions-collect.html "collect\(\)") as part of a [`groupBy()`](functions-groupby.html "groupBy\(\)") operation **

##### Query

logscale
    
    
    groupBy(client_ip, function=session(maxpause=1m, collect([url])))

##### Introduction

In this example, the [`collect()`](functions-collect.html "collect\(\)") function is used to collect visitors, each visitor defined as non-active after one minute. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(client_ip, function=session(maxpause=1m, collect([url])))

Collects visitors (URLs), each visitor defined as non-active after one minute and returns the results in an array named client_ip. A count of the events is returned in a _count field. 

  3. Event Result set.




##### Summary and Results

The query is used to collect fields from multiple events into one event. This query analyzes user behavior by grouping events into sessions for each unique client IP address. It then collects all URLs accessed during each session. Collecting should be used on smaller data sets to create a list (or set, or map, or whatever) when you actually need a list object explicitly (for example, in order to pass it on to some other API). This analysis is valuable for understanding user engagement, and identifying potential security issues based on unusual browsing patterns. Using [`collect()`](functions-collect.html "collect\(\)") on larger data set may cause out of memory as it returns the entire data set. 

#### Collect and Group Events by Specified Field - Example 2

**Collect and group events by specified field using[`collect()`](functions-collect.html "collect\(\)") as part of a [`groupBy()`](functions-groupby.html "groupBy\(\)") operation **

##### Query

logscale
    
    
    LocalAddressIP4 = * RemoteAddressIP4 = * aip = *
    | groupBy([LocalAddressIP4, RemoteAddressIP4], function=([count(aip, as=aipCount, distinct=true), collect([aip])]))

##### Introduction

In this example, the [`collect()`](functions-collect.html "collect\(\)") function is used to collect fields from multiple events. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         LocalAddressIP4 = * RemoteAddressIP4 = * aip = *

Filters for all events where the fields LocalAddressIP4, RemoteAddressIP4 and aip are all present. The actual values in these fields do not matter; the query just checks for their existence. 

  3. logscale
         
         | groupBy([LocalAddressIP4, RemoteAddressIP4], function=([count(aip, as=aipCount, distinct=true), collect([aip])]))

Groups the returned results in arrays named LocalAddressIP4 and RemoteAddressIP4, collects all the AIPs (Adaptive Internet Protocol) into an array and performs a count on the field aip. The count of the AIP values is returned in a new field named aipCount. 

  4. Event Result set.




##### Summary and Results

The query is used to collect fields from multiple events into one event. Collecting should be used on smaller data sets to create a list (or set, or map, or whatever) when you actually need a list object explicitly (for example, in order to pass it on to some other API). Using [`collect()`](functions-collect.html "collect\(\)") on larger data set may cause out of memory as it returns the entire data set. The query is useful for network connection analysis and for identifying potential threats. 

Sample output might look like this: 

LocalAddressIP4| RemoteAddressIP4| aipCount| aip  
---|---|---|---  
192.168.1.100| 203.0.113.50| 3| [10.0.0.1, 10.0.0.2, 10.0.0.3]  
10.0.0.5| 198.51.100.75| 1| [172.16.0.1]  
172.16.0.10| 8.8.8.8| 5| [192.0.2.1, 192.0.2.2, 192.0.2.3, 192.0.2.4, 192.0.2.5]
