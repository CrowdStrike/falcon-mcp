# series() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-series.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`series()`](functions-series.html "series\(\)")

Collects a series of values for the selected fields from multiple events into one (or more) events. Combined with [`groupBy()`](functions-groupby.html "groupBy\(\)"), this can be used to gather data from transactions by some identity field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`collect`_](functions-series.html#query-functions-series-collect)[a]| array of strings| required |  |  Names of the fields to keep.   
[_`endmatch`_](functions-series.html#query-functions-series-endmatch)|  filter| optional[b] |  |  A filter query inside `{}` to match the end of a transaction (applied to the event as a whole), for example, `{ /session end:/ }`. Even with this parameter specified, "partial" sessions which do not include an `end` event are output — unlike what happens with the _`startmatch`_ parameter, _`endmatch`_ does not cause any event to be ignored.   
[_`maxduration`_](functions-series.html#query-functions-series-maxduration)|  relative-time| optional[[b]](functions-series.html#ftn.table-functions-series-optparamfn) |  |  Maximum duration of a transaction (for example, 5min), specified as a [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax").   
[_`maxpause`_](functions-series.html#query-functions-series-maxpause)|  relative-time| optional[[b]](functions-series.html#ftn.table-functions-series-optparamfn) |  |  Maximum time between events in a transaction (for example, 10s), specified as a [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax").   
[_`memlimit`_](functions-series.html#query-functions-series-memlimit)|  string| optional[[b]](functions-series.html#ftn.table-functions-series-optparamfn) |  |  Limit on number of bytes of memory consumed by each series invocation (defaults to 1KiB). When used with the parameters startmatch, endmatch, maxpause and maxduration to produce multiple sub-series, this parameter controls the memory usage of the entire sequence of series, not each individual one. When series is used inside a [`groupBy()`](functions-groupby.html "groupBy\(\)"), this parameter only limits the memory consumption per group. So if the [`groupBy()`](functions-groupby.html "groupBy\(\)") is limited to 50,000 groups each using 1KB, the combined upper limit would be 50MB.   
|  | **Minimum**| `1`|   
|  | **Maximum**| [`1024`](functions-series.html#query-functions-series-memlimit-max-1024)|   
|  | **Controlling Variables**  
|  | [`MAX_SERIES_MEMLIMIT`](https://library.humio.com/falcon-logscale-self-hosted/envar-max_series_memlimit.html)|   
[_`separator`_](functions-series.html#query-functions-series-separator)|  string| optional[[b]](functions-series.html#ftn.table-functions-series-optparamfn) | `\n`|  String used to separate multiple values.   
[_`startmatch`_](functions-series.html#query-functions-series-startmatch)|  filter| optional[[b]](functions-series.html#ftn.table-functions-series-optparamfn) |  |  A filter query inside `{}` to match the start of a transaction (applied to the event as a whole), for example, `{ /session start:/ }`. With this parameter specified, any event coming before the first `start` event, or in between an `end` event and the `start` event that follows, is not part of any session and is therefore ignored — all sessions include exactly one `start` event.   
[a] The parameter name [_`collect`_](functions-series.html#query-functions-series-collect) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`collect`_](functions-series.html#query-functions-series-collect) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     series(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     series(collect=["value"])
> 
> These examples show basic structure only.

### [`series()`](functions-series.html "series\(\)") Function Operation

For example, given an access log, you can collect the series of methods for a given url like this: 

logscale
    
    
    url="/some/url"
    | series([method], separator=";")

This produces a single event: 

Field |  Example |  Description   
---|---|---  
[@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) |  145245466 |  Timestamp of the first event arriving.   
_duration |  1245 |  Timespan (in milliseconds) of the series of events included in this series. If the series contains just one field value the value of _duration will be 0.   
method |  GET;POST;GET;GET;DELETE |  Time-ordered series of values for the method field.   
  
Because the value of the collected fields may be rather large, the memory consumption of this function can be controlled using the _`memlimit`_ parameter. 

Using the similar data source as above, you can also emit a single event for each user "visit" as defined above by, for example, a maximum pause of 5 minutes between HTTP accesses like this: 

logscale
    
    
    url="/some/url"
    | series([method], separator=";", maxpause=5min)

This may produce two (or more) events: 

Field |  Example |  Description   
---|---|---  
[@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) |  145245466 |  Timestamp of the first event arriving.   
_duration |  512 |  Timespan (in milliseconds) of the series of events included in this series. If the series contains just one field value the value of _duration will be 0.   
`method` |  GET;POST;GET |  Time-ordered series of values for the method field.   
  
Field |  Example |  Description   
---|---|---  
[@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) |  149256978 |  Timestamp of the first event in the second batch.   
_duration |  251 |  Timespan (in milliseconds) of the series of events included in this series.   
`method` |  GET;DELETE |  Time-ordered series of values for the method field in the second batch.   
  
Because this function can use a lot of memory to gather all the data making up the collected field values, it controls memory usage at runtime using the _`memlimit`_ parameter. 

### [`series()`](functions-series.html "series\(\)") Syntax Examples

In an access log, collect the series of methods used for a given URL. 

logscale
    
    
    url="/some/url"
    | series([method], separator=";")

Aggregate series of website visits, each visitor defined as non-active after 1 minute. 

logscale
    
    
    groupBy(client_ip, function=series(maxpause=1m, collect=[url], memlimit=1KB))

Aggregate series of auth logs, starting a new series for each login attempt. 

logscale
    
    
    groupBy(userID, function=series(collect=[@rawstring], startmatch={ /Login attempt:/ }))

Aggregate series of auth logs, ending each series with a failed login attempt. 

logscale
    
    
    groupBy(userID, function=series(collect=[@rawstring], endmatch={ /Failed Login/ }))
