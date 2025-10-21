# sort() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-sort.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`sort()`](functions-sort.html "sort\(\)")

The [`sort()`](functions-sort.html "sort\(\)") query function is used to sort events based on a given field — or fields. Events can be sorted by multiple fields by setting the field parameter to an array of field names (for example, between square-brackets in a comma-separated list). Likewise, the order and type of each field can be specified by setting the [_`order`_](functions-sort.html#query-functions-sort-order) and [_`type`_](functions-sort.html#query-functions-sort-type) parameters to arrays. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-sort.html#query-functions-sort-field)[a]| array of strings| optional[b] |  |  The fields by which to sort events.   
[_`limit`_](functions-sort.html#query-functions-sort-limit)|  integer| optional[[b]](functions-sort.html#ftn.table-functions-sort-optparamfn) | `200`|  The argument given to this parameter determines the limit on the number of events included in the result of the function. The default argument is `default`. The maximum is controlled by the [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) dynamic configuration, which is [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) by default. If the argument is `max` (`limit=max`), then the value of [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) is used.   
|  |  | **Values**  
|  |  | [`max`](functions-sort.html#query-functions-sort-limit-option-max)| An alias to use the maximum limit set by [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)  
|  | **Maximum**| `200,000`|   
|  | **Controlling Variables**  
|  | [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)|  **Variable default:**`200,000 rows`  
[ _`order`_](functions-sort.html#query-functions-sort-order)|  array of strings| optional[[b]](functions-sort.html#ftn.table-functions-sort-optparamfn) | [`desc`](functions-sort.html#query-functions-sort-order-option-desc)|  The order in which to sort.   
|  |  | **Values**  
|  |  | [`asc`](functions-sort.html#query-functions-sort-order-option-asc)| Sort ascending  
|  |  | [`desc`](functions-sort.html#query-functions-sort-order-option-desc)| Sort descending  
[ _`reverse`_](functions-sort.html#query-functions-sort-reverse) (deprecated)| boolean| optional[[b]](functions-sort.html#ftn.table-functions-sort-optparamfn) | [`false`](functions-sort.html#query-functions-sort-reverse-option-false)|  Whether to sort in descending order. This parameter is deprecated: use [_`order`_](functions-sort.html#query-functions-sort-order) instead. (**deprecated in 1.100**)  
|  |  | **Values**  
|  |  | [`false`](functions-sort.html#query-functions-sort-reverse-option-false)| Sort ascending  
|  |  | [`true`](functions-sort.html#query-functions-sort-reverse-option-true)| Sort descending  
[ _`type`_](functions-sort.html#query-functions-sort-type)|  array of strings| optional[[b]](functions-sort.html#ftn.table-functions-sort-optparamfn) | [`number`](functions-sort.html#query-functions-sort-type-option-number)|  Set the data type of the fields to influence the sorting order.   
|  |  | **Values**  
|  |  | [`hex`](functions-sort.html#query-functions-sort-type-option-hex)| Treat the field as a hexadecimal value and sort in numerical order  
|  |  | [`number`](functions-sort.html#query-functions-sort-type-option-number)| Treat the field as numerical and sort in numerical order  
|  |  | [`string`](functions-sort.html#query-functions-sort-type-option-string)| Treat the field as string values and sort alphabetical  
[a] The parameter name [_`field`_](functions-sort.html#query-functions-sort-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-sort.html#query-functions-sort-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     sort(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     sort(field=["value"])
> 
> These examples show basic structure only.

### [`sort()`](functions-sort.html "sort\(\)") Function Operation

If the [_`order`_](functions-sort.html#query-functions-sort-order) or [_`type`_](functions-sort.html#query-functions-sort-type) parameter is a single value, all fields are sorted with the same order or type. 

Setting the [_`type`_](functions-sort.html#query-functions-sort-type) field tells [`sort()`](functions-sort.html "sort\(\)") how to compare the individual values, either using lexicographical order (for example, [`string`](functions-sort.html#query-functions-sort-type-option-string)), numerical magnitude (for example, [`number`](functions-sort.html#query-functions-sort-type-option-number), [`hex`](functions-sort.html#query-functions-sort-type-option-hex)). The [`hex`](functions-sort.html#query-functions-sort-type-option-hex) argument supports numbers as strings starting with either `0x`, `0X`, or no prefix. 

### Warning

Sorting is performed in memory. For optimum performance avoid sorting large numbers of events. Perform filtering first and sort the results, or use aggregation to simplify the event list before sorting. Putting [`sort()`](functions-sort.html "sort\(\)") last in a query, after an aggregating function, offers the best performance. 

### [`sort()`](functions-sort.html "sort\(\)") Syntax Examples

As an example, suppose you have LogScale ingesting data from a web server and want to get a list of referring domains and sub-domains. That is to say, the URLs without the path and web page from which it came (for example, just `www.example.com` from `http://www.example.com/sales/great-sites.html`). Suppose further that you want a count of each referrer and want to sort them alphabetically in reverse order — because we're fickle like that. Below is an example of how that might be done: 

logscale Syntax
    
    
    regex(regex="/.*/(?<ref_url>.+?)(/
    | $)", field=referrer)
    | groupBy(ref_url)
    | sort(ref_url, type=string, order=desc, limit=12)

In the first line here, we're using the [`regex()`](functions-regex.html "regex\(\)") function to extract just the first part of the URL, dropping everything after the domain and first slash. On the second line we're using [`groupBy()`](functions-groupby.html "groupBy\(\)") to group on each referrer (for example, `ref_url`) and counting them. If we hadn't stripped out the base URL from the first line, we might have multiple entries for each domain. See the [`regex()`](functions-regex.html "regex\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") reference pages for more information on those query functions. 

In the third line of the query above, notice the parameters for the [`sort()`](functions-sort.html "sort\(\)") function. First is the new field ref_url we created in the first line, then [_`type`_](functions-sort.html#query-functions-sort-type) parameter to specify the values sorted may include characters or numbers. The second is how to order the results: in this case, in descending order. Last is the [_`limit`_](functions-sort.html#query-functions-sort-limit) parameter to limit the results to the first twelve in the sorted list of results. The table below shows the results. 

ref_url| _count  
---|---  
www.zabotkin.ru| 14  
www.tangblog.top| 1  
www.skidn.com| 1  
www.klfd.net| 1  
www.iopt.pro| 42  
www.google.com.au| 1  
www.google.com| 11  
www.bing.com| 3  
  
To sort events by ascending or descending value, use the [_`order`_](functions-sort.html#query-functions-sort-order) parameter, for example: 

logscale Syntax
    
    
    groupBy(ref_url)
    | sort(ref_url, type=string, order=asc, limit=12)

The output has been ordered using a string based (for example, alphabetical) sorting method. 

The [_`limit`_](functions-sort.html#query-functions-sort-limit) parameter to [`sort()`](functions-sort.html "sort\(\)") limits the number of rows returned by the function after the sort has been completed. For example, to sort metrics by the repository name and then output the top entry: 

Syntax
    
    
    name=datasource-count
    |groupBy([repo])
    |sort(field=_count,type=number,order=desc,limit=1)

The above query works by sorting the grouped counts (in the _count field), explicitly setting the type to `number` and then sorting by high to lowest (descending order). 

To sort events by ascending or descending value, use the [_`order`_](functions-sort.html#query-functions-sort-order) parameter, for example: 

logscale Syntax
    
    
    groupBy(ref_url)
    | sort(ref_url, type=string, order=desc, limit=12)

When using multiple fields, supply a corresponding array to [_`order`_](functions-sort.html#query-functions-sort-order) parameter as the [_`field`_](functions-sort.html#query-functions-sort-field) parameter, for example: 

logscale Syntax
    
    
    groupBy([ref_url,method])
    | sort([ref_url,method], type=string, order=[desc,asc], limit=12)

### [`sort()`](functions-sort.html "sort\(\)") Examples

Click + next to an example below to get the full details.

#### Analyze User Sessions Based on Click Activity

**Analyzes user sessions based on users click activity using the[`session()`](functions-session.html "session\(\)") function **

##### Query

logscale
    
    
    groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))
    | sort(clicks)

##### Introduction

In this example, the [`session()`](functions-session.html "session\(\)") function is used to analyze user sessions based on users click activity. The [`session()`](functions-session.html "session\(\)") function groups events by a given timespan. 

Example incoming data might look like this: 

timestamp| cookie_id| action_type| page_url| user_agent  
---|---|---|---|---  
2025-05-15 05:30:00| user123| pageview| /home| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:15| user123| click| /products| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:30| user123| click| /product/item1| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:00| user123| click| /cart| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:30| user123| click| /checkout| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:35:00| user456| pageview| /home| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:35:30| user456| click| /about| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:36:00| user456| click| /contact| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:38:00| user789| pageview| /home| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
2025-05-15 05:38:30| user789| click| /products| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))

Groups events by the field cookie_id (unique user identifier) and creates sessions with 15-minute inactivity timeout (the default value of the [_`maxpause`_](functions-session.html#query-functions-session-maxpause) parameter), then makes a count of each event in a session returning the result in a new field named clicks. 

  3. logscale
         
         | sort(clicks)

Sorts the results by number of clicks (default is descending order). 

  4. Event Result set.




##### Summary and Results

The query is used to analyze user sessions based on the users click activity. The query is useful, for example, to identify most/least active user sessions, detect potential automated behavior or just to understand user engagement levels. 

Sample output from the incoming example data: 

cookie_id| clicks  
---|---  
user123| 5  
user456| 3  
user789| 2  
  
Note that each row represents an event (either pageview or click). 

#### Calculate Query Cost for All Users by Repository

**Search across multiple repositories to calculate query costs for all users by repository using[`sort()`](functions-sort.html "sort\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") functions **

##### Query

logscale
    
    
    #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"
     | groupBy(repo, initiatingUser, totalLiveCost, totalStaticCost)
     | sort([totalLiveCost, totalStaticCost])

##### Introduction

In this example, the query uses [`sort()`](functions-sort.html "sort\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") functions to find query costs. The query filters logs in [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `c.h.j.RunningQueriesLoggerJob`, searching for the specific value `Highest Cost query`. 

Example incoming data might look like this: 

#type| #kind| class| message| timestamp| dataspace| initiatingUser| totalLiveCost| totalStaticCost| deltaTotalCost| repo  
---|---|---|---|---|---|---|---|---|---|---  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:30:00Z| production| john.doe| 1500| 800| 2300| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:31:00Z| development| jane.smith| 2000| 1200| 3200| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:32:00Z| staging| bob.wilson| 1000| 500| 1500| infra-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:33:00Z| production| john.doe| 1800| 900| 2700| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:34:00Z| development| jane.smith| 2500| 1300| 3800| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:35:00Z| staging| alice.cooper| 1200| 600| 1800| infra-logs  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"

Filters for Humio internal logs containing `c.h.j. RunningQueriesLoggerJob` in the class field and where the value in the message field is equal to `Highest Cost query`. 

  3. logscale
         
         | groupBy(repo, initiatingUser, totalLiveCost, totalStaticCost)

Groups the results by the repo field, the initiatingUser field, and by both cost types (the fields totalLiveCost, totalStaticCost), and returns a count in a field named _count. 

  4. logscale
         
         | sort([totalLiveCost, totalStaticCost])

Sorts the results by both the totalLiveCost field and the totalStaticCost field, in descending order by default. 

  5. Event Result set.




##### Summary and Results

The query is used to search across multiple repositories and output query costs for all users by repository. The query returns the count in a field named _count. Use this query to focus on live and static costs separately. 

Sample output from the incoming example data: 

repo| initiatingUser| totalLiveCost| totalStaticCost| _count  
---|---|---|---|---  
app-logs| jane.smith| 2000| 1200| 1  
security-logs| john.doe| 1500| 800| 1  
infra-logs| bob.wilson| 1000| 500| 1  
  
#### Calculate Total Network Bandwidth Per Host

**Analyze network traffic patterns using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function with [`sum()`](functions-sum.html "sum\(\)") **

##### Query

logscale
    
    
    event_simpleName="NetworkConnectStats"
    groupBy([ComputerName], function=[
            sum(field="BytesReceived", as=InboundTraffic),
            sum(field="BytesSent", as=OutboundTraffic)
            ])
    TotalTraffic := InboundTraffic + OutboundTraffic
    sort(field="TotalTraffic", order="desc")

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") is used with nested [`sum()`](functions-sum.html "sum\(\)") functions to calculate total inbound and outbound network traffic per host, followed by calculating the total bandwidth consumption. 

Example incoming data might look like this: 

@timestamp| event_simpleName| ComputerName| BytesReceived| BytesSent  
---|---|---|---|---  
1686837825000| NetworkConnectStats| DESKTOP-A1| 15000000| 8500000  
1686837825000| NetworkConnectStats| DESKTOP-A1| 8900000| 4200000  
1686837825000| NetworkConnectStats| LAPTOP-B2| 25000000| 12000000  
1686837826000| NetworkConnectStats| SERVER-C3| 95000000| 45000000  
1686837826000| NetworkConnectStats| DESKTOP-A1| 12000000| 6800000  
1686837826000| NetworkConnectStats| LAPTOP-B2| 18000000| 9500000  
1686837827000| NetworkConnectStats| SERVER-C3| 85000000| 42000000  
1686837827000| NetworkConnectStats| DESKTOP-D4| 5000000| 2800000  
1686837827000| NetworkConnectStats| LAPTOP-B2| 22000000| 11000000  
1686837828000| NetworkConnectStats| SERVER-C3| 105000000| 52000000  
1686837828000| NetworkConnectStats| DESKTOP-D4| 6500000| 3200000  
1686837828000| NetworkConnectStats| DESKTOP-A1| 9800000| 5100000  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         event_simpleName="NetworkConnectStats"

Filters events to include only those where event_simpleName equals `NetworkConnectStats`. 

  3. logscale
         
         groupBy([ComputerName], function=[
                 sum(field="BytesReceived", as=InboundTraffic),
                 sum(field="BytesSent", as=OutboundTraffic)
                 ])

Groups the data by the ComputerName field and calculates two aggregate values: the sum of BytesReceived stored in a field named InboundTraffic, and the sum of BytesSent stored in a field named OutboundTraffic. 

  4. logscale
         
         TotalTraffic := InboundTraffic + OutboundTraffic

Creates a new field named TotalTraffic containing the values from the InboundTraffic and OutboundTraffic fields. 

  5. logscale
         
         sort(field="TotalTraffic", order="desc")

Sorts the results based on the TotalTraffic field in descending order ([_`order`_](functions-sort.html#query-functions-sort-order)=`desc`), showing hosts with highest bandwidth consumption first. 

  6. Event Result set.




##### Summary and Results

The query is used to analyze network bandwidth consumption patterns across different hosts in the network. 

This query is useful, for example, to identify hosts consuming excessive bandwidth, monitor network usage patterns, or detect potential network-intensive applications or anomalies. 

Sample output from the incoming example data: 

ComputerName| InboundTraffic| OutboundTraffic| TotalTraffic  
---|---|---|---  
SERVER-C3| 285000000| 139000000| 424000000  
LAPTOP-B2| 65000000| 32500000| 97500000  
DESKTOP-A1| 45700000| 24600000| 70300000  
DESKTOP-D4| 11500000| 6000000| 17500000  
  
Note that the traffic values are in bytes and that each row represents the aggregated traffic for a unique host 

#### Filter Out Fields With No Value

**Filter out fields with no values from search results**

##### Query

logscale
    
    
    method=GET
    groupBy(field=[method, statuscode], function=count(as=method_total))
    sort([method, statuscode], order=asc)
    FieldName!=""

##### Introduction

It is possible to filter out on fields with no values in a given returned search result. In this example, all statuscode fields containing no value is filtered out from the final search result. 

Example incoming data might look like this: 

method| statuscode| method_total  
---|---|---  
GET| <no value>| 10  
GET| 200| 32492  
GET| 301| 1  
GET| 304| 113  
GET| 403| 9  
GET| 404| 132  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         method=GET

Filters for all events with methods of the type `GET`. 

  3. logscale
         
         groupBy(field=[method, statuscode], function=count(as=method_total))

Groups the returned results into a method field and a statuscode field and makes a count of the events in a new field named method_total. 

  4. logscale
         
         sort([method, statuscode], order=asc)

Sorts the returned results in ascending order. 

  5. logscale
         
         FieldName!=""

Excludes all events where one of the fields do not contain a value. 

  6. Event Result set.




##### Summary and Results

The query is used to filter out fields not containing any values from the returned search result. 

Sample output from the incoming example data: 

method| statuscode| method_total  
---|---|---  
GET| 200| 32492  
GET| 301| 1  
GET| 304| 113  
GET| 403| 9  
GET| 404| 132  
  
#### Find Least Common Values of a Field

**Find the least common values of a field using the[`sort()`](functions-sort.html "sort\(\)") function with [`count()`](functions-count.html "count\(\)") **

##### Query

logscale
    
    
    groupby([type,kind], limit=max, function=count())
    | sort(_count, order=asc)

##### Introduction

The [`sort()`](functions-sort.html "sort\(\)") function can be used to sort values in a field bottom up. This is the opposite of the [`top()`](functions-top.html "top\(\)") function, that can be used to find the most common values of a field in a set of events. 

In this example, the [`sort()`](functions-sort.html "sort\(\)") function is used to find the least common values of a field. Types of parsers used (type field) are grouped with their LogScale logging types (kind field) to find the least common values when searching for events of, for example, kinds `metrics`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupby([type,kind], limit=max, function=count())

Groups the event set by the fields type and kind. For each unique combination of type and kind, it then counts the number of events, and returns the results in a field named _count. 

The parameter [_`limit`_](functions-groupby.html#query-functions-groupby-limit) is set to `max` to return all counts, as the purpose of this example is to find the least common values of a field. 

  3. logscale
         
         | sort(_count, order=asc)

Sorts the returned results in ascending order from the least common combinations to the most common combinations of type and kind. 

  4. Event Result set.




##### Summary and Results

The query is used to find the least common values of a field in a set of events, in this example, identifying the least and most common type/kind combinations in an event set. Identifying rare combinations of type and kind could indicate unusual events or potential security issues. This type of query is useful in various scenarios, particularly for data analysis and understanding patterns in event sets.
