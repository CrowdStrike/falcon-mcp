# defineTable() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-definetable.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`defineTable()`](functions-definetable.html "defineTable\(\)")

Executes a subquery that generates an in-memory, ad-hoc table based on its results. The ad-hoc table can be joined with the results of the primary query using the [`match()`](functions-match.html "match\(\)") function. 

### Note

  * Place all [`defineTable()`](functions-definetable.html "defineTable\(\)") declarations in the query preamble before other query operations (except if using the [`setTimeInterval()`](functions-settimeinterval.html "setTimeInterval\(\)") function also, then [`defineTable()`](functions-definetable.html "defineTable\(\)") must be placed after this function). 

  * Write [`defineTable()`](functions-definetable.html "defineTable\(\)") declarations at the top level of your query. Do not nest them inside functions or subqueries. 

  * It is possible to reference previously defined tables in subsequent [`defineTable()`](functions-definetable.html "defineTable\(\)") declarations. 

  * Each query supports up to 10 ad-hoc tables. 

  * Do not create circular references between tables. 




For more information on using Ad-hoc tables, see [Using Ad-hoc Tables](query-joins-methods-adhoc-tables.html "Using Ad-hoc Tables"). 

[`defineTable()`](functions-definetable.html "defineTable\(\)") is the recommended alternative to the [`join()`](functions-join.html "join\(\)") function, allowing for easier query writing of complex joins. For more explanations on the benefits of using ad-hoc tables with [`defineTable()`](functions-definetable.html "defineTable\(\)") instead of [`join()`](functions-join.html "join\(\)"), see [Ad-hoc Tables vs. join()](query-joins-methods-adhoc-tables.html#query-joins-methods-adhoc-tables-join "Ad-hoc Tables vs. join\(\)"). 

Combined with [`match()`](functions-match.html "match\(\)") and [`readFile()`](functions-readfile.html "readFile\(\)") query functions, [`defineTable()`](functions-definetable.html "defineTable\(\)") can be used to create several types of join-like queries — see [`defineTable()` Examples](functions-definetable.html#functions-definetable-examples "defineTable\(\) Examples"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`end`_](functions-definetable.html#query-functions-definetable-end)|  string| optional[a] | `same as primary query`|  End of time interval of subquery: milliseconds since UNIX epoch or a timestamp relative to the primary query's end time using [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax"). For example: if [_`start=7d`_](functions-definetable.html#query-functions-definetable-start) and the main query's end time is `2024-03-25 14:00:00`, then the [`defineTable()`](functions-definetable.html "defineTable\(\)") subquery should would use the time `2024-03-18 14:00:00`.   
[_`include`_](functions-definetable.html#query-functions-definetable-include)|  array of strings| required |  |  Fields to include as columns in the temporary table. If set to `*` all fields will be included.   
[_`name`_](functions-definetable.html#query-functions-definetable-name)|  string| required |  |  Name of the ad-hoc table that is generated. Used to reference the table in other functions within the primary query.   
[_`query`_](functions-definetable.html#query-functions-definetable-query)[b]| function| required |  |  Subquery used to generate the ad-hoc table.   
[_`start`_](functions-definetable.html#query-functions-definetable-start)|  string| optional[[a]](functions-definetable.html#ftn.table-functions-definetable-optparamfn) | `same as primary query`|  Start of time interval of subquery: milliseconds since UNIX epoch or a timestamp relative to the primary query's end time using [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax"). For example: if [_`start=7d`_](functions-definetable.html#query-functions-definetable-start) and the main query's end time is `2024-03-25 14:00:00`, then the [`defineTable()`](functions-definetable.html "defineTable\(\)") subquery would use the time `2024-03-18 14:00:00`  
[_`view`_](functions-definetable.html#query-functions-definetable-view)|  string| optional[[a]](functions-definetable.html#ftn.table-functions-definetable-optparamfn) | `same as primary query`|  View in which to perform the subquery.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`query`_](functions-definetable.html#query-functions-definetable-query) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`query`_](functions-definetable.html#query-functions-definetable-query) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     defineTable("value",include=["value"],name="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     defineTable(query="value",include=["value"],name="value")
> 
> These examples show basic structure only.

### [`defineTable()`](functions-definetable.html "defineTable\(\)") Function Operation

The [`defineTable()`](functions-definetable.html "defineTable\(\)") function has specific implementation and operational considerations, outlined below. 

  * [`defineTable()`](functions-definetable.html "defineTable\(\)") cannot be used with the [`join()`](functions-join.html "join\(\)"), [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") or [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") functions. 

  * To ensure optimal performance when using [`defineTable()`](functions-definetable.html "defineTable\(\)"), follow the best practice described at [Ad-hoc Tables Optimization](query-joins-methods-adhoc-tables.html#query-joins-methods-adhoc-tables-optimization "Ad-hoc Tables Optimization"). 

  * For more information on the different methods of creating join queries — including ad-hoc tables with the [`defineTable()`](functions-definetable.html "defineTable\(\)") function — see [Join Methods](query-joins-methods.html "Join Methods"). 

  * ### Important

When using [`defineTable()`](functions-definetable.html "defineTable\(\)"), be aware that ad-hoc tables are not supported in [Triggers](automated-alerts.html "Triggers"), for the reasons explained at [Ad-hoc Tables in Live Queries](query-joins-methods-adhoc-tables.html#query-joins-methods-adhoc-tables-live-query "Ad-hoc Tables in Live Queries"). Use [Scheduled searches](automated-alerts.html#trigger_types-scheduled-searches) instead. 

  * Time specification for the [_`start`_](functions-definetable.html#query-functions-definetable-start) and [_`end`_](functions-definetable.html#query-functions-definetable-end) must be related to the start and end time of the main query using the [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax"). If the parameters are not used, the query will default to using the start and end times of the main query. 

For example, given a main query with an end time of 2025-07-15 12:00:00 (Noon on 15th July 2025) to 2025-07-15 15:00:00 (3pm on 15th July 2025): 

    * 7 days earlier start time `start=7d` would set Noon on 8th July 2025 

    * 1 day earlier start time `start=1d` would set Noon on 14th July 2025 

    * 1 day earlier start time `start=24h` would set Noon on 14th July 2025 

    * 6 hours earlier start time `start=6h` would set 6am on 14th July 2025 

Using an absolute time will not set the right value for comparison for the table data. 




### [`defineTable()`](functions-definetable.html "defineTable\(\)") Syntax Examples

The function's signature combined with [`match()`](functions-match.html "match\(\)"): 

logscale Syntax
    
    
    defineTable(query={a=hello}, name="tablename", include=[col1,col2,col3])
    | match(table="tablename",field=fieldname, column=col1)

For example, to match email data within the same view: 

Raw Events

email=bob@example.com firstname=bob lastname=thomas  
---  
loginemail=bob@example.com action=register  
  
Perform a subquery and a primary query: 

logscale Syntax
    
    
    defineTable(query={email=*}, name="emails", include=[email,firstname, lastname])
    | match(table="emails", field=loginemail, column=email)

The first query in the pipeline is the subquery used for table definition. The second query in the pipeline is the primary query that uses [`match()`](functions-match.html "match\(\)"). 

The following example query combines information about the `ProcessRollUp2` and `NetworkListenIP4` to find processes that have created listeners on a port. 

  1. This is the full query: 

logscale
         
         defineTable(query={#event_simpleName=NetworkListenIP4 LocalPort<1024 LocalPort!=0}, name="network_listener", include=[ContextProcessId,LocalAddressIP4, LocalPort])
         | #event_simpleName=ProcessRollup2
         | match(table="network_listener",field=TargetProcessId,column=ContextProcessId)

  2. The subquery with [`defineTable()`](functions-definetable.html "defineTable\(\)") generates a result table named `network_listener`: 

ContextProcessId |  LocalAddressIP4 |  LocalPort   
---|---|---  
123 |  172.16.254.1 |  1010   
456 |  172.19.254.1 |  2020   
789 |  190.16.254.1 |  3030   
  
  3. The second item in the pipeline filters #event_simpleName field to only take the `ProcessRollUp2` value. 

  4. [`match()`](functions-match.html "match\(\)") joins the results of the `network_listener` ad-hoc table with the primary query, by matching: 

     * TargetProcessId field from the primary query 

     * ContextProcessId column field from the ad-hoc, generated table. 




### [`defineTable()`](functions-definetable.html "defineTable\(\)") Examples

Click + next to an example below to get the full details.

#### Filter For Items Not Part of Data Set Using [`defineTable()`](functions-definetable.html "defineTable\(\)")

**Find the set difference using the[`defineTable()`](functions-definetable.html "defineTable\(\)") function with `!match()` **

##### Query

logscale
    
    
    defineTable(
    name=session_ids,
    query={#repo=B session_id=*},
    include=session_id
    )
    #repo=A session_id=*
    | !match(table=session_ids, field=session_id)

##### Introduction

In this example, the [`defineTable()`](functions-definetable.html "defineTable\(\)") function is used with a `!match()` to search and find all session IDs from data set A that are not found in data set B. 

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
         
         defineTable(
         name=session_ids,
         query={#repo=B session_id=*},
         include=session_id
         )

Generates an ad-hoc table from repository `B` named `session_ids` and filters on all events in repository `B` that contain the field session_id. 

  3. logscale
         
         #repo=A session_id=*

Filters for all events from repository `A`, that contain a session_id field. 

  4. logscale
         
         | !match(table=session_ids, field=session_id)

Performs a negated match with repository `B`, and returns sessions that exist in repository `A` but not in repository `B`. The negation operator is used to return non-matching results. 

  5. Event Result set.




##### Summary and Results

The query is used to find the set difference between two repositories. This is, for example, useful for identifying sync issues or performing data consistency checks. Or just to make a cross-repository comparison. 

For more information, see also [_Query Joins and Lookups_](query-joins.html "Query Joins and Lookups")

Sample output from the incoming example data: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:10:00Z| 123458| mike.jones| upload| failed  
2025-04-01T07:15:00Z| 123459| sara.wilson| login| success  
  
#### Perform a Left Join Query to Combine Two Datasets

****

##### Query

logscale
    
    
    defineTable(name="users_table",query={orgId=1},include=[username, name])
    | operation=createdFile
    | match(table=users_table, field=username, strict=false)
    | select([username, name])

##### Introduction

In this example, the [`defineTable()`](functions-definetable.html "defineTable\(\)") function is used as a left join query to extract and combine information from two different datasets. 

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| name| orgId  
---|---|---  
user1| John Doe| 1  
user2| Jane Doe| 1  
user3| Bob Smith| 2  
  
and the other event set: 

username| operation  
---|---  
user1| createdFile  
user2| deletedFile  
user3| createdFile  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         defineTable(name="users_table",query={orgId=1},include=[username, name])

Generates an ad-hoc table named `users_table` that has the fields username and name and includes users where orgId field equals `1`. 

  3. logscale
         
         | operation=createdFile

Filters on the field operation for users who performed the action of creating a file by looking for the value `createdFile`. 

  4. logscale
         
         | match(table=users_table, field=username, strict=false)

Joins with `users_table` table. 

  5. logscale
         
         | select([username, name])

Selects the username and name fields to be displayed from the event set. 

  6. Event Result set.




##### Summary and Results

The result will output two events: 

username| name  
---|---  
user1| John Doe  
user3| no value  
  
where user3 has no value since this user is not included in the `users_table` table `user2` (not belonging to orgId=1). 

#### Perform a Nested Join Query to Combine Two Datasets and Two Tables

****

##### Query

logscale
    
    
    defineTable(name="organization_table",query={orgId=1},include=[username, orgId],view=organizations)
    | defineTable(name="users_table",query={match(table=organization_table, field=username)},include=[username, name])
    | operation=createdFile
    | match(table=users_table, field=username)
    | select([username, name])

##### Introduction

Similar to the [inner join](https://library.humio.com/examples/examples-define-table-inner.html) example, [`defineTable()`](functions-definetable.html "defineTable\(\)") first creates a separate table for organizations belonging to a different view, which is then matched against a users' table as a nested-like join. 

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| orgId  
---|---  
user1| 1  
user2| 1  
user3| 2  
  
and the other event set: 

username| name  
---|---  
user1| John Doe  
user2| Jane Doe  
user3| Bob Smith  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         defineTable(name="organization_table",query={orgId=1},include=[username, orgId],view=organizations)

Generates an ad-hoc table named `organization_table` that has the fields username and orgId and includes users where orgId field equals `1` from the `organizations` view. 

  3. logscale
         
         | defineTable(name="users_table",query={match(table=organization_table, field=username)},include=[username, name])

Generates an ad-hoc table named `users_table` that has the fields username and name and enriches rows with orgId=1 from `organization_table`

  4. logscale
         
         | operation=createdFile

Filters on the field operation for users who performed the action of creating a file by looking for the value `createdFile`. 

  5. logscale
         
         | match(table=users_table, field=username)

Joins with `users_table` table, to filter out users who are not from orgId=1 and to enrich with the users' names. 

  6. logscale
         
         | select([username, name])

Selects the username and name fields to be displayed from the event set. 

  7. Event Result set.




##### Summary and Results

The result will output one event: 

username| name  
---|---  
user1| John Doe  
  
#### Perform a Right Join Query to Combine Two Datasets

****

##### Query

logscale
    
    
    defineTable(name="users",query={orgId=1},include=[username, name])
    | defineTable(name="operations",query={*},include=[username, operation])
    | readFile(users)
    | match(operations, field=username, strict=false)
    | select([username, operation])

##### Introduction

In this example, the [`defineTable()`](functions-definetable.html "defineTable\(\)") function is used as a right join query to extract and combine information from two different datasets. 

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| name| orgId  
---|---|---  
user1| John Doe| 1  
user2| Jane Doe| 1  
user3| Bob Smith| 2  
  
and the other event set: 

username| operation  
---|---  
user1| createdFile  
user3| createdFile  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         defineTable(name="users",query={orgId=1},include=[username, name])

Generates an ad-hoc table named `users` that has the fields username and name and includes users where orgId field equals `1`. 

  3. logscale
         
         | defineTable(name="operations",query={*},include=[username, operation])

Defines a new ad-hoc table that uses all the fields (username and operation) in a table named `operations`. 

  4. logscale
         
         | readFile(users)

Reads the `users` ad-hoc table as events using [`readFile()`](functions-readfile.html "readFile\(\)"). 

  5. logscale
         
         | match(operations, field=username, strict=false)

Matches the events that have a matching operation from the `operations` table with the `users` table using the username as the common field. Events are not filtered if the events do not match, (implying a right join), by using [_`strict=false`_](functions-match.html#query-functions-match-strict)

  6. logscale
         
         | select([username, operation])

Selects the username and operation fields to be displayed from the event set. 

  7. Event Result set.




##### Summary and Results

The result will output two events: 

username| operation  
---|---  
user1| createdFile  
user2| no value  
  
Note that in the event set all operations have been included even when there is no match between the username field, resulting in the `no value` for `user2`. If [_`strict=true`_](functions-match.html#query-functions-match-strict) had been used to the [`match()`](functions-match.html "match\(\)") function, then the event for `user2` would not have been outputted. 

#### Perform an Inner Join Query to Combine Two Datasets

****

##### Query

logscale
    
    
    defineTable(name="users_table",query={orgId=1},include=[username, name])
    | orgId=1
    | operation=createdFile
    | match(table=users_table, field=username)
    | select([username, name])

##### Introduction

In this example, the [`defineTable()`](functions-definetable.html "defineTable\(\)") function is used as an inner join query to extract and combine information from two different datasets. 

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| name| orgId  
---|---|---  
user1| John Doe| 1  
user2,Jane Doe",1|  |   
user3| Bob Smith| 2  
  
and the other event set: 

username| operation  
---|---  
user1| createdFile  
user2| deletedFile  
user3| createdFile  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         defineTable(name="users_table",query={orgId=1},include=[username, name])

Generates an ad-hoc table named `users_table` that has the fields username and name and filters used where the orgId field equals `1`. 

  3. logscale
         
         | orgId=1

Selects only users from the orgId where the value equals `1`. 

  4. logscale
         
         | operation=createdFile

Filters on the field operation for users who performed the action of creating a file by looking for the value `createdFile`. 

  5. logscale
         
         | match(table=users_table, field=username)

Joins the filtered events (users that created a file in organization 1) using the username field with the `users_table` table. 

  6. logscale
         
         | select([username, name])

Selects the username and name fields to be displayed in the result set. 

  7. Event Result set.




##### Summary and Results

The result will output one event: 

username| name  
---|---  
user1| John Doe  
  
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

#### Using Ad-hoc Table With CSV File

****

##### Query

logscale
    
    
    defineTable(name="users_table",query={match(file=organizations.csv, field=username)
    | orgId=1 },include=[username, name])
    | operation=createdFile
    | match(table=users_table, field=username)
    | select([username, name])

##### Introduction

In this example, the [`defineTable()`](functions-definetable.html "defineTable\(\)") is used to extract and combine information from two different datasets, with the mapping between username and orgId stored in a CSV file. The example file `organizations.csv` has the following content: 

CSV
    
    
    username,orgId
    user1,1
    user2,1
    user3,2

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| name  
---|---  
user1| John Doe  
user2| Jane Doe  
user3| Bob Smith  
  
and the other event set: 

username| operation  
---|---  
user1| createdFile  
user2| deletedFile  
user3| createdFile  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         defineTable(name="users_table",query={match(file=organizations.csv, field=username)
         | orgId=1 },include=[username, name])

Generates an ad-hoc table named `users_table` that has the fields username and name and includes users where orgId field equals `1`. Then uses [`match()`](functions-match.html "match\(\)") to enrich rows with orgId from `organizations.csv` file. 

  3. logscale
         
         | operation=createdFile

Filters on the field operation for users who performed the action of creating a file by looking for the value `createdFile`. 

  4. logscale
         
         | match(table=users_table, field=username)

Joins the username field with the `users_table` table, to filter out users who are not from orgId=1 and to enrich with the users' names. 

  5. logscale
         
         | select([username, name])

Selects the username and name fields to be displayed from the event set. 

  6. Event Result set.




##### Summary and Results

The result will output one event: 

username| name  
---|---  
user1| John Doe
