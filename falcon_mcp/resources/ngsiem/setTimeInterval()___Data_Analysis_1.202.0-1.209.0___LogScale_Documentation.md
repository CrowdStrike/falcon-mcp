# setTimeInterval() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-settimeinterval.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)")

[`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") can be used to set the query's time interval and related time settings from within the query string. When used, the query time specified in the query string will override the settings from the UI or query API. 

For more information about time specification options, see [Search API Time Specification](https://library.humio.com/logscale-api/api-search-timespec.html). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`end`_](functions-settimeinterval.html#query-functions-settimeinterval-end)|  string,time point| optional[a] | `now`|  End time of query. When specified, it overrides the end time from the query API.   
[_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start)[b]| string,time point| required |  |  Start time of query. When specified, it overrides the start time from the query API.   
[_`timezone`_](functions-settimeinterval.html#query-functions-settimeinterval-timezone)|  string,time zone name| optional[[a]](functions-settimeinterval.html#ftn.table-functions-settimeinterval-optparamfn) |  |  Time zone name. When specified, overrides the timezone set from the query API. For a list of timezone names, see [the table “Supported Timezones”](syntax-time-timezones.html#table_supported-timezones "Table: Supported Timezones").   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     setTimeInterval(1d)
> 
> and:
> 
> logscale Syntax
>     
>     
>     setTimeInterval(start=1d)
> 
> These examples show basic structure only.

### [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") Function Operation

Using [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") offers several advantages: 

  * Query users can specify time ranges directly in query strings. The feature enables copying and sharing query strings with other users, who can recreate the search in different views and/or clusters (with different URLs). 

  * Dashboard creators can specify time ranges in query strings. The feature allows setting the static time range for the widgets. 




This is a metadata query function that does not process events. It is only used for setting the time interval and related metadata from within the query instead of through the [Query Jobs API](https://library.humio.com/logscale-api/api-search-query-create.html) or the UI. 

Using [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") affects both the API and the UI, as follows. 

  * The [_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start) and [_`end`_](functions-settimeinterval.html#query-functions-settimeinterval-end) parameters of the function override the [Query Jobs API](https://library.humio.com/logscale-api/api-search-query-create.html)`end` and `start` fields, meaning that a query like this: 

logscale
        
        groupBy([status_code, ip]

with `start=7d` and `end=1d` set in `QueryJobInput`, is equivalent to query: 

logscale
        
        setTimeInterval(start=7d, end=1d) 
        | groupBy([status_code, ip]

  * When the [Time field](searching-data-expand-timeframe.html#searching-data-expand-timeframe-time-field) selection is set to @ingesttimestamp in the UI, then the query will be submitted to the [QueryJobInput](https://library.humio.com/logscale-api/api-search-query-create.html) with input [useIngestTime](https://library.humio.com/logscale-api/api-search-query-create.html#table_queryjobinput-queryjobinput-useingesttime) equal to `true`. In this scenario, the [_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start) and [_`end`_](functions-settimeinterval.html#query-functions-settimeinterval-end) parameters of [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") will override the [ingestStart](https://library.humio.com/logscale-api/api-search-query-create.html#table_queryjobinput-queryjobinput-ingeststart) and [ingestEnd](https://library.humio.com/logscale-api/api-search-query-create.html#table_queryjobinput-queryjobinput-ingestend) API fields. 

  * When the [Time field](searching-data-expand-timeframe.html#searching-data-expand-timeframe-time-field) selection is set to @timestamp in the UI, then the query will be submitted to the [QueryJobInput](https://library.humio.com/logscale-api/api-search-query-create.html) with input [useIngestTime](https://library.humio.com/logscale-api/api-search-query-create.html#table_queryjobinput-queryjobinput-useingesttime) equal to `false`. In this scenario, the [_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start) and [_`end`_](functions-settimeinterval.html#query-functions-settimeinterval-end) parameters of [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") will override the [start](https://library.humio.com/logscale-api/api-search-query-create.html#table_queryjobinput-queryjobinput-start) and [end](https://library.humio.com/logscale-api/api-search-query-create.html#table_queryjobinput-queryjobinput-end) API fields. 




Using [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") also overrides the time controls in the UI. See [Change Time Interval](searching-data-expand-timeframe.html#time-selector-function "Warning") and [Shared Time Selector](dashboards-time-shared-time-selector.html#dashboards-shared-time-function "Warning") for more information. 

### Validation Rules/Known Limitations

The [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function requires specific validation rules for correct usage. 

  * Must appear in the preamble of the query — that is, before any other functions, filters, free-text searches, etc. 

  * Must appear before any [`defineTable()`](functions-definetable.html "defineTable\(\)") definitions. 

  * Must appear at most once in a query. 

  * Cannot appear inside [`join()`](functions-join.html "join\(\)")/[`defineTable()`](functions-definetable.html "defineTable\(\)") subqueries. To set a different time range for the ad-hoc table/join subquery, use the _`start`_ and _`end`_ parameters that are supported in these functions. 

  * Same restrictions as the API time interval apply, that is: 

    * In a live query `start` must be relative, and `end` must be `now`

    * If the user has search limitations (for example, trial users can only search 7 days back), these limitations still apply 

  * [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") is only supported in ad-hoc searches and on dashboards. In particular, [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") is not supported in: 

    * [Triggers](automated.html "Automation") (aggregate alerts, filter alerts, legacy alerts, scheduled searches) 

    * [Parsers](parsers.html "Parse Data")

    * [Event Forwarders](https://library.humio.com/falcon-logscale-self-hosted/ingesting-data-event-forwarders.html)

    * [Redact Events API](https://library.humio.com/logscale-api/api-redact-events.html)

    * Filter prefix of a query such as repository filters, user filters, group filters (like any other query functions, which are equally not supported) 

    * [Dashboard filters](dashboards-interactive-filters.html "Apply Dashboard Filters")




### [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") Examples

Click + next to an example below to get the full details.

#### Set Relative Time Interval From Within Query

**Set the relative time interval and related metadata from within the query instead of through the QueryJobs API or UI**

##### Query

logscale
    
    
    setTimeInterval(start=7d, end=1d)

##### Introduction

In this example, the [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function is used to define a new relative time interval before running an ad-hoc query. 

For more information about time specification options, see [Search API Time Specification](https://library.humio.com/logscale-api/api-search-timespec.html). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         setTimeInterval(start=7d, end=1d)

Sets a time interval to start 7 days ago from now and to end 1 day ago from now. As the timezone is not specified, it uses the system's default. 

It is possible to explicitly set a timezone instead of using the system's default, in this example, the timezone is explicitly set to `Europe/Copenhagen`: `setTimeInterval(start="1w@d", end="now@d", timezone="Europe/Copenhagen")`

  3. Event Result set.




##### Summary and Results

This query demonstrates how to use [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") to define the timespan from within the query instead of through the QueryJobs API or UI. 

For an example of using absolute time, see [Set Specific Time Interval Based on Raw Epoch Timestamps From Within Query](https://library.humio.com/examples/examples-settimeinterval-specify-time-range.html). 

#### Set Specific Time Interval Based on Raw Epoch Timestamps From Within Query

**Set a specific time interval based on raw epoch timestamps from within the query instead of through the QueryJobs API or UI**

##### Query

logscale
    
    
    setTimeInterval(start=1746054000000, end=1746780124517)
    | "#event_simpleName" = ProcessRollup2

##### Introduction

In this example, the [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function is used to define a new time interval based on the epoch times `1746054000000` and `1746780124517` and return events of the type ProcessRollup2. 

For more information about time specification options, see [Search API Time Specification](https://library.humio.com/logscale-api/api-search-timespec.html). 

Example incoming data might look like this: 

timestamp| event_simpleName| ProcessId| CommandLine| ImageFileName| UserName| aid  
---|---|---|---|---|---|---  
1746054100000| ProcessRollup2| 4567| /usr/bin/python3 script.py| /usr/bin/python3| john.doe| a1b2c3d4e5f6  
1746054200000| ProcessRollup2| 4568| notepad.exe file.txt| C:\Windows\notepad.exe| jane.smith| b2c3d4e5f6g7  
1746054300000| ProcessRollup2| 4569| cmd.exe /c dir| C:\Windows\System32\cmd.exe| admin.user| c3d4e5f6g7h8  
1746054400000| ImageLoadv2| 4570| explorer.exe| C:\Windows\explorer.exe| john.doe| d4e5f6g7h8i9  
1746054500000| ProcessRollup2| 4571| powershell.exe -nologo| C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| system| e5f6g7h8i9j0  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         setTimeInterval(start=1746054000000, end=1746780124517)

Sets a time interval in raw epoch time to start at `1746054000000` and end at `1746780124517`. The timestamps are in Unix epoch milliseconds. 

Searches within the specified time period. 

  3. logscale
         
         | "#event_simpleName" = ProcessRollup2

Filters for events where the values in the field event_simpleName is of the type ProcessRollup2. The ProcessRollup2 events represent process execution/creation events in CrowdStrike. 

  4. Event Result set.




##### Summary and Results

The query is used to return only ProcessRollup2 events that occurred during a specific timeframe defined in Epochs per millisecond. 

This query demonstrates how to use [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") to define the timespan in Epoch times from within the query instead of through the QueryJobs API or UI. 

For an example of using relative time, see [Set Relative Time Interval From Within Query](https://library.humio.com/examples/examples-settimeinterval-basic.html). 

Sample output from the incoming example data: 

timestamp| event_simpleName| ProcessId| CommandLine| ImageFileName| UserName| aid  
---|---|---|---|---|---|---  
1746054100000| ProcessRollup2| 4567| /usr/bin/python3 script.py| /usr/bin/python3| john.doe| a1b2c3d4e5f6  
1746054200000| ProcessRollup2| 4568| notepad.exe file.txt| C:\Windows\notepad.exe| jane.smith| b2c3d4e5f6g7  
1746054300000| ProcessRollup2| 4569| cmd.exe /c dir| C:\Windows\System32\cmd.exe| admin.user| c3d4e5f6g7h8  
1746054500000| ProcessRollup2| 4571| powershell.exe -nologo| C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| system| e5f6g7h8i9j0  
  
The query only returns rows 1, 2, 3, and 5 since row 4 has a different event_simpleName (ImageLoadv2). 

#### Set Time Interval From Within Query with [`defineTable()`](functions-definetable.html "defineTable\(\)")

**Set the time interval and related metadata from within the query instead of through the test QueryJobs API or UI using the[`defineTable()`](functions-definetable.html "defineTable\(\)") function **

##### Query

logscale
    
    
    setTimeInterval(start="1h", end="30min")
    | defineTable(
    start=7d,
    end=1d,
    query={...},
    name="ended_queries")
    | match(table="ended_queries", field=queryID, strict=true)

##### Introduction

In this example, the [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function is used with the [`defineTable()`](functions-definetable.html "defineTable\(\)") function to define a new time interval for the subqueries, before running this. 

Note that the [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function must appear before any [`defineTable()`](functions-definetable.html "defineTable\(\)") definitions and only one time in a query. 

For more information about time specification options, see [Search API Time Specification](https://library.humio.com/logscale-api/api-search-timespec.html). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         setTimeInterval(start="1h", end="30min")

Recalls the [`defineTable()`](functions-definetable.html "defineTable\(\)") subquery time interval. This means that the subquery will start at `7d+30min`, and will end at `1d+30min`. 

  3. logscale
         
         | defineTable(
         start=7d,
         end=1d,
         query={...},
         name="ended_queries")

Generates an ad-hoc table named `ended_queries` and computes the relative time points to the primary query's time end time. This means that the subquery will start at `7d+30min`, and will end at `1d+30min`

  4. logscale
         
         | match(table="ended_queries", field=queryID, strict=true)

Joins the filtered events where the value equals `queryID` with the ended_queries table. 

  5. Event Result set.




##### Summary and Results

This query demonstrates how to use [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") to define the timespan for a defined table query.
