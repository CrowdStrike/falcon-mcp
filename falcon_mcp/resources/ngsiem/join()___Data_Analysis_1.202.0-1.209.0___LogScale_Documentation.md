# join() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-join.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`join()`](functions-join.html "join\(\)")

Joins two LogScale searches. When joining two searches, you need to define the keys/fields that are used to match up results. This is done using the [_`field=name`_](functions-join.html#query-functions-join-field) or [_`field=[name,name,...]`_](functions-join.html#query-functions-join-field) parameter. If you want to join on a single field name, you can use the syntax: 

logscale Syntax
    
    
    fieldName =~ join(...)

to specify the field. 

If the subquery has a different field that you want to match against, then use the parameter [_`key=[name1,name2,...]`_](functions-join.html#query-functions-join-key) to designate the names of keys inside the subquery. The value of keys defaults to the value of field. 

[`join()`](functions-join.html "join\(\)") is a filter function which in the default [_`mode=inner`_](functions-join.html#query-functions-join-mode) lets the events through that match on the join keys. If you specify [_`mode=left`_](functions-join.html#query-functions-join-mode) then events that do not match the join key(s) will also be let through. 

If you specify [_`include=[field, field, ...]`_](functions-join.html#query-functions-join-include) then those fields are extracted from the result of the subquery, and added to matching events. For events in the subquery that do not have one or more of the named include fields, the output will be the empty string. 

Using the parameter [_`max=N`_](functions-join.html#query-functions-join-max) (which defaults to `max=1`) you can specify how many rows/events are picked up in the subquery. If a subquery has multiple events with the same join key, then up to max rows are emitted. 

You can use the parameters [_`start`_](functions-join.html#query-functions-join-start) and [_`end`_](functions-join.html#query-functions-join-end) to specify an alternative time interval for the query. The parameter view can be used to direct the subquery to run in a different repository or view, and the [_`live=true|false`_](functions-join.html#query-functions-join-live) parameter can be used to control if the subquery runs as a live query. The defaults for all these parameters are inherited from the primary query containing the `join(...)` usage. 

The [`join()`](functions-join.html "join\(\)") function also has a concept of a maximum size of the resultset of the inner query specified with the [_`limit=100000`_](functions-join.html#query-functions-join-limit) parameter. 

Warning

The [`join()`](functions-join.html "join\(\)") function does two passes over the data and should not be used as part of a live query. The two passes consist of the primary query and the subquery; as two separate queries the sets of data on which they are executed may be different leading to inconsistent results. 

When used in a live query, the query will be run in a repeated mode instead, in which the server chooses the repetition interval based on the resources used by the function. 

This can impact the liveness of the query, in that long-running repeated queries can be throttled, and thus be less live than expected. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`end`_](functions-join.html#query-functions-join-end)|  string| optional[a] | `End of main query`|  Specifies either the timestamp relative to the main query's end (for example, `end=2h` will be two hours before the end of the main query) or an absolute timestamp in milliseconds since UTC.   
[_`field`_](functions-join.html#query-functions-join-field)|  array of strings| required |  |  Specifies which field in the event (log line) must match the given column value.   
[_`include`_](functions-join.html#query-functions-join-include)|  array of strings| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | `none`|  Specifies columns to include from the subquery.   
[_`key`_](functions-join.html#query-functions-join-key)|  array of strings| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) |  |  Specifies which fields of the subquery to join on. Defaults to the value of the [_`field`_](functions-join.html#query-functions-join-field) parameter.   
[_`limit`_](functions-join.html#query-functions-join-limit)|  number| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | `100000`|  Specifies the maximum number of rows in the subquery.   
|  | **Minimum**| `1`|   
|  | **Maximum**| [`200000`](functions-join.html#query-functions-join-limit-max-200000)|   
[ _`live`_](functions-join.html#query-functions-join-live)|  boolean| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | `Same as main query`|  Control if the subquery runs as live or static query.   
[_`max`_](functions-join.html#query-functions-join-max)|  integer| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | `1`|  Maximum number of events found in subquery if several share join key.   
[_`mode`_](functions-join.html#query-functions-join-mode)|  string| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | [`inner`](functions-join.html#query-functions-join-mode-option-inner)|  Specifies the mode (inner or left) of the join.   
|  |  | **Values**  
|  |  | [`inner`](functions-join.html#query-functions-join-mode-option-inner)| Perform an inner join; return only results that match in both queries  
|  |  | [`left`](functions-join.html#query-functions-join-mode-option-left)| Perform a left join, all values from the parent query are included, matched to any corresponding events in subquery.  
[_`query`_](functions-join.html#query-functions-join-query)[b]| function| required |  |  The subquery to execute producing the values to join with.   
[_`repo`_](functions-join.html#query-functions-join-repo)|  string| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | `Repo of main query`|  Specify which view/repo in which to perform the subquery.   
[_`start`_](functions-join.html#query-functions-join-start)|  string| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | `Start of main query`|  Specifies either the timestamp relative to the main query's end (for example, `start=2h` will be two hours before the end of the main query) or an absolute timestamp in milliseconds since UTC.   
[_`view`_](functions-join.html#query-functions-join-view)|  string| optional[[a]](functions-join.html#ftn.table-functions-join-optparamfn) | `View of main query`|  Specify which view/repo in which to perform the subquery.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`query`_](functions-join.html#query-functions-join-query) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`query`_](functions-join.html#query-functions-join-query) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     join("value",field=["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     join(query="value",field=["value"])
> 
> These examples show basic structure only.

Hide negatable operation for this function

Show negatable operation for this function

> Negatable Function Operation
> 
> This function is negatable, implying the inverse of the result. For example:
> 
> logscale Syntax
>     
>     
>     !join()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not join()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

Find some examples at [`join()` Syntax](query-joins-methods-join.html#query-joins-methods-join-syntax "join\(\) Syntax") section. 

### [`join()`](functions-join.html "join\(\)") Examples

Click + next to an example below to get the full details.

#### Filter For Items Not Part of Data Set Using `!join()`

**Find the set difference using the[`join()`](functions-join.html "join\(\)") function with negation **

##### Query

logscale
    
    
    #repo=A session_id=*
    | !join(query={#repo=B session_id=*}, field=session_id, key=session_id)

##### Introduction

In this example, the [`join()`](functions-join.html "join\(\)") function is used with a negation to search and find all session IDs from data set A that are not found in data set B. 

![](images/venn-seta-not-setb.png)  
---  
  
Example incoming data from repository A might look like this: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:00:00Z| 123456| john.doe| login| success  
2025-04-01T07:05:00Z| 123457| jane.smith| download| success  
2025-04-01T07:10:00Z| 123458| mike.jones| upload| failed  
2025-04-01T07:15:00Z| 123459| sara.wilson| login| success  
2025-04-01T07:20:00Z| 123460| bob.brown| logout| success  
  
Example incoming data from repository B might look like this: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:00:00Z| 123456| john.doe| login| success  
2025-04-01T07:05:00Z| 123457| jane.smith| download| success  
2025-04-01T07:20:00Z| 123460| bob.brown| logout| success  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #repo=A session_id=*

Filters for all events from repository `A`, that have a session_id field. 

  3. logscale
         
         | !join(query={#repo=B session_id=*}, field=session_id, key=session_id)

Performs a negated join with repository `B`, and returns sessions that exist in repository `A` but not in repository `B`. The negation operator is used to make it an anti-join operation. 

LogScale recommends using the [`defineTable()`](functions-definetable.html "defineTable\(\)") function with `!match()` instead of negated join. See example [Filter For Items Not Part of Data Set Using `defineTable()` ](https://library.humio.com/examples/examples-definetable-negated-set-difference.html)

  4. Event Result set.




##### Summary and Results

The query is used to find the set difference between two repositories. This is, for example, useful for identifying sync issues or performing data consistency checks. Or just to make a cross-repository comparison. 

For more information, see also [_Query Joins and Lookups_](query-joins.html "Query Joins and Lookups")

Sample output from the incoming example data: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:10:00Z| 123458| mike.jones| upload| failed  
2025-04-01T07:15:00Z| 123459| sara.wilson| login| success  
  
#### Join Log Events with Reference Data

**Combining events from different queries using the[`join()`](functions-join.html "join\(\)") function **

##### Query

logscale
    
    
    event_type=auth
    join({repo=user_details}, field=department, key=user_id, mode=inner)

##### Introduction

In this example, the [`join()`](functions-join.html "join\(\)") function is used to combine authentication events with user details from a reference repository. 

Example incoming data might look like this: 

@timestamp| event_type| user_id| action| status  
---|---|---|---|---  
2025-09-01T10:00:00Z| auth| U123| login| success  
2025-09-01T10:00:05Z| auth| U456| login| failed  
2025-09-01T10:00:10Z| auth| U789| password_change| success  
2025-09-01T10:00:15Z| auth| U123| logout| success  
2025-09-01T10:00:20Z| auth| U456| login| failed  
2025-09-01T10:00:25Z| auth| U789| login| success  
2025-09-01T10:00:30Z| auth| U123| login| success  
2025-09-01T10:00:35Z| auth| U999| login| failed  
2025-09-01T10:00:40Z| auth| U456| password_reset| success  
2025-09-01T10:00:45Z| auth| U123| logout| success  
  
And the reference data in the `user_details` repository looks like this: 

@timestamp| user_id| department| role| location  
---|---|---|---|---  
2025-09-01T00:00:00Z| U123| IT| admin| London  
2025-09-01T00:00:00Z| U456| Sales| user| Paris  
2025-09-01T00:00:00Z| U789| HR| manager| Berlin  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         event_type=auth

Filters the primary query to include only authentication events where event_type equals `auth`. 

  3. logscale
         
         join({repo=user_details}, field=department, key=user_id, mode=inner)

Performs an inner join with the `user_details` repository. The join: 

     * Uses [_`repo`_](functions-join.html#query-functions-join-repo)=`user_details` to specify the repository containing reference data. 

     * Uses [_`field`_](functions-join.html#query-functions-join-field)=`department` to specify which field to include from the reference data. 

     * Uses [_`key`_](functions-join.html#query-functions-join-key)=`user_id` to specify the field to join on. 

     * Uses [_`mode`_](functions-join.html#query-functions-join-mode)=`inner` to only include events where there is a match in both datasets. 

  4. Event Result set.




##### Summary and Results

The query is used to enrich authentication events with user department information from a reference repository. 

This query is useful, for example, to analyze authentication patterns by department or to investigate security incidents with additional user context. 

Sample output from the incoming example data: 

@timestamp| event_type| user_id| action| status| department  
---|---|---|---|---|---  
2025-09-01T10:00:00Z| auth| U123| login| success| IT  
2025-09-01T10:00:05Z| auth| U456| login| failed| Sales  
2025-09-01T10:00:10Z| auth| U789| password_change| success| HR  
2025-09-01T10:00:15Z| auth| U123| logout| success| IT  
2025-09-01T10:00:20Z| auth| U456| login| failed| Sales  
2025-09-01T10:00:25Z| auth| U789| login| success| HR  
2025-09-01T10:00:30Z| auth| U123| login| success| IT  
2025-09-01T10:00:40Z| auth| U456| password_reset| success| Sales  
2025-09-01T10:00:45Z| auth| U123| logout| success| IT  
  
Note that the event with user_id=`U999` is not included in the output because it has no matching record in the reference data (inner join behavior). 

For other [`join()`](functions-join.html "join\(\)") examples, see also [`join()` Syntax](query-joins-methods-join.html#query-joins-methods-join-syntax "join\(\) Syntax"). 

#### Preview Content in a Lookup File With [`readFile()`](functions-readfile.html "readFile\(\)") and Filter With ![`join()`](functions-join.html "join\(\)")

**Preview content in a lookup file in the search portion of a repo and filter for specific data with the ![`join()`](functions-join.html "join\(\)") function **

##### Query

logscale
    
    
    readFile("host_names.csv")
    | !join(query={groupBy(host_name)}, field=host_name, key=host_name, include=[host_name, id])

##### Introduction

In this example, the [`readFile()`](functions-readfile.html "readFile\(\)") function is used to look up a host_names.csv file, and then filter for host names that do not send any logs. 

Example incoming data might look like this: 
    
    
    |--------------------|
    | host_name, host_id |
    | DESKTOP-VSKPBK8, 1 |
    | FINANCE, 2         |
    | homer-xubuntu, 3   |
    | logger, 4          |
    | DESKTOP-1, 5       |
    | DESKTOP-2, 6       |
    | DESKTOP-3, 7       |
    |--------------------|

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         readFile("host_names.csv")

Displays the content of the .csv file. 

  3. logscale
         
         | !join(query={groupBy(host_name)}, field=host_name, key=host_name, include=[host_name, id])

Filters for host names that do not send any logs. 

  4. Event Result set.




##### Summary and Results

The query is used to preview content in CSV Lookup Files, and then filter for host names that do not send any logs. 

Sample output from the incoming example data: 

host_id| host_name  
---|---  
5| DESKTOP-1  
6| DESKTOP-2  
7| DESKTOP-3
