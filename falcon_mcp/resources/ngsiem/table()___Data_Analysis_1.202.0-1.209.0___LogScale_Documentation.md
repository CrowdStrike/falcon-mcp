# table() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-table.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`table()`](functions-table.html "table\(\)")

The [`table()`](functions-table.html "table\(\)") function displays query results in a table, allowing to specify the list of fields to include in the table. 

The [`table()`](functions-table.html "table\(\)") function is an aggregate function and does as follows: 

  * Sorts columns in the table based on specified field order. 
  * Aggregates events based on the _`limit`_ parameter. It will limit the number of events returned using the _`limit`_ parameter. 
  * Sorts results according to the _`sortby`_ parameter. 



For large data exports, consider using the [`select()`](functions-select.html "select\(\)") function instead. The [`select()`](functions-select.html "select\(\)") function provides similar tabular output but without row limits or sorting constraints in streaming queries. For standard queries, the implied [`tail(200)`](functions-tail.html "tail\(\)") would be applied. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`fields`_](functions-table.html#query-functions-table-fields)[a]| array of strings| required |  |  The names of the fields to select.   
[_`limit`_](functions-table.html#query-functions-table-limit)|  number| optional[b] | `200`|  The argument given to this parameter determines the limit on the number of rows included in the result of the function. The maximum is controlled by the [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) dynamic configuration, which is [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) by default. If the argument is `max` (`limit=max`), then the value of [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html) is used.   
|  |  | **Values**  
|  |  | [`max`](functions-table.html#query-functions-table-limit-option-max)| An alias to use the maximum limit set by [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)  
|  | **Maximum**| `200,000`|   
|  | **Controlling Variables**  
|  | [`StateRowLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-state_row_limit.html)|  **Variable default:**`200,000 rows`  
[ _`order`_](functions-table.html#query-functions-table-order)|  array of strings| optional[[b]](functions-table.html#ftn.table-functions-table-optparamfn) | [`desc`](functions-table.html#query-functions-table-order-option-desc)|  Order to sort in.   
|  |  | **Values**  
|  |  | [`asc`](functions-table.html#query-functions-table-order-option-asc)| Ascending (A-Z, 0-9) order  
|  |  | [`desc`](functions-table.html#query-functions-table-order-option-desc)| Descending (Z-A, 9-0) order  
[ _`reverse`_](functions-table.html#query-functions-table-reverse)|  boolean| optional[[b]](functions-table.html#ftn.table-functions-table-optparamfn) |  |  Whether to sort in descending order. Deprecated: prefer [_`order`_](functions-table.html#query-functions-table-order) instead.   
[_`sortby`_](functions-table.html#query-functions-table-sortby)|  array of strings| optional[[b]](functions-table.html#ftn.table-functions-table-optparamfn) | `@timestamp`|  Names of fields to sort by.   
[_`type`_](functions-table.html#query-functions-table-type)|  array of strings| optional[[b]](functions-table.html#ftn.table-functions-table-optparamfn) | [`number`](functions-table.html#query-functions-table-type-option-number)|  Type of the fields to sort.   
|  |  | **Values**  
|  |  | [`any`](functions-table.html#query-functions-table-type-option-any)| Any fields. (**deprecated in 1.125**)  
|  |  | [`hex`](functions-table.html#query-functions-table-type-option-hex)| Hexadecimal fields  
|  |  | [`number`](functions-table.html#query-functions-table-type-option-number)| Numerical fields  
|  |  | [`string`](functions-table.html#query-functions-table-type-option-string)| String fields  
[a] The parameter name [_`fields`_](functions-table.html#query-functions-table-fields) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`fields`_](functions-table.html#query-functions-table-fields) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     table(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     table(fields=["value"])
> 
> These examples show basic structure only.

### [`table()`](functions-table.html "table\(\)") Syntax Examples

Create a table of HTTP GET methods displaying the fields statuscode and responsetime: 

logscale
    
    
    method=GET
    | table([statuscode, responsetime])

Display the 50 slowest requests by name and responsetime: 

logscale
    
    
    table([name, responsetime], sortby=responsetime, limit=50, order=asc)

### [`table()`](functions-table.html "table\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Query Costs by User and Repository in a Single Field

**Calculate query costs by user across multiple repositories, showing the repository/user as a single field**

##### Query

logscale
    
    
    #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"
    | repoUser:= format("%s/%s", field=[dataspace, initiatingUser])
    | top(repoUser, sum=deltaTotalCost, as=cost)
    |table([cost, repoUser], sortby=cost)

##### Introduction

In this example, the query filter events in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `c.h.j.RunningQueriesLoggerJob`, searching for the specific value `Highest Cost query`. The query then combines the results in a new field repoUser. The query then uses [`top()`](functions-top.html "top\(\)") and [`table()`](functions-table.html "table\(\)") functions to aggregate and display the results. 

Example incoming data might look like this: 

#type| #kind| class| message| timestamp| dataspace| initiatingUser| totalLiveCost| totalStaticCost| deltaTotalCost| repo  
---|---|---|---|---|---|---|---|---|---|---  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:30:00Z| production| john.doe| 1500| 800| 2300| security-logs  
humio| logs c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:31:00Z| development| jane.smith| 2000| 1200| 3200| app-logs|   
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
         
         | repoUser:= format("%s/%s", field=[dataspace, initiatingUser])

Combines the fields dataspace and initiatingUser with a `/` separator, and then assigns the combined value to a new field named repoUser. Example of combined value: `dataspace/username`. 

  4. logscale
         
         | top(repoUser, sum=deltaTotalCost, as=cost)

Finds the most common values in the field repoUser, makes a sum of the field deltaTotalCost, and returns the results in a new field named cost. 

  5. logscale
         
         |table([cost, repoUser], sortby=cost)

Displays the results in a table with fields `cost` and `repoUser`, sorted by the column `cost`. 

  6. Event Result set.




##### Summary and Results

The query is used to search across multiple repositories and calculate query costs per user, by combining costs and showing the repository/user as a single field. 

Sample output from the incoming example data: 

cost| repoUser  
---|---  
3200| development/jane.smith  
2300| production/john.doe  
1500| staging/bob.wilson  
  
#### Convert Values Between Units

**Convert file size and transfer time units using the[`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function **

##### Query

logscale
    
    
    unit:convert(field=file_size, from="B", to="MB")
    | unit:convert(field=transfer_time, from="ms", to="s")
    | table([file_size, transfer_time])

##### Introduction

In this example, the [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function is used to convert file sizes and transfer times units. The [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function automatically handles the mathematical conversion between units, making it easier to work with different measurement scales in the event set. 

Note that any unit is supported in LogScale. 

Example incoming data might look like this: 

timestamp| file_name| file_size| transfer_time| status  
---|---|---|---|---  
2025-05-15 05:30:00| doc1.pdf| 1048576| 3500| complete  
2025-05-15 05:31:00| img1.jpg| 2097152| 4200| complete  
2025-05-15 05:32:00| video1.mp4| 5242880| 12000| complete  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         unit:convert(field=file_size, from="B", to="MB")

Converts file sizes from Bytes (B) to Megabytes (MB). 

  3. logscale
         
         | unit:convert(field=transfer_time, from="ms", to="s")

Converts transfer times from milliseconds (ms) to seconds (s) 

  4. logscale
         
         | table([file_size, transfer_time])

Displays the result of the fields file_size and transfer_time in a table. 

  5. Event Result set.




##### Summary and Results

The query is used to convert file sizes and transfer times units. A table showing file sizes and transfer times is, for example, useful to spot unusually large file transfers, to identify slow transfers or bottlenecks (for debugging). 

The [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function is useful to standardize the units for better comparison and make data more readable. 

Note that any unit is supported in LogScale. For more examples, see [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)"). 

Sample output from the incoming example data: 

file_name| file_size| transfer_time  
---|---|---  
doc1.pdf| 1.0| 3.5  
img1.jpg| 2.0| 4.2  
video1.mp4| 5.0| 12.0  
  
#### Display User Account Deletion Events in Table Format

**Create a table showing deleted user accounts using the[`table()`](functions-table.html "table\(\)") function **

##### Query

logscale
    
    
    #event_simpleName=UserAccountDeleted
    aid=?aid
    table([aid, UserName, UserId], limit=1000)

##### Introduction

In this example, the [`table()`](functions-table.html "table\(\)") function is used to create a structured view of deleted user accounts, displaying the account ID, [username](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html), and user ID. 

Example incoming data might look like this: 

@timestamp| event_simpleName| aid| UserName| UserId  
---|---|---|---|---  
2025-10-06 08:00:00| UserAccountDeleted| abc123| john.doe| UID001  
2025-10-06 08:15:30| UserAccountDeleted| def456| jane.smith| UID002  
2025-10-06 09:20:45| UserAccountDeleted| ghi789| bob.wilson| UID003  
2025-10-06 10:05:15| UserAccountDeleted| jkl012| sarah.jones| UID004  
2025-10-06 11:30:00| UserAccountDeleted| mno345| mike.brown| UID005  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #event_simpleName=UserAccountDeleted

Filters events where event_simpleName equals `UserAccountDeleted`

  3. logscale
         
         aid=?aid

Filters results based on a specific account ID using the parameter aid. 

`aid=` is the parameter name and `?aid` is a placeholder for the actual aid value. The question mark (`?`) indicates a parameter placeholder that will be replaced with an actual value during execution. 

  4. logscale
         
         table([aid, UserName, UserId], limit=1000)

Creates a table displaying the fields aid, [UserName](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html), and UserId. The [`table()`](functions-table.html "table\(\)") function includes a [_`limit`_](functions-table.html#query-functions-table-limit) parameter set to `1000` rows to prevent excessive output. 

  5. Event Result set.




##### Summary and Results

The query is used to create a structured table view of user account deletion events, showing essential account information. 

This query is useful, for example, to monitor user account deletions, audit user management activities, or investigate security incidents related to account removals. 

Sample output from the incoming example data: 

aid| UserName| UserId  
---|---|---  
abc123| john.doe| UID001  
def456| jane.smith| UID002  
ghi789| bob.wilson| UID003  
jkl012| sarah.jones| UID004  
mno345| mike.brown| UID005
