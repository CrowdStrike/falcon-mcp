# readFile() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-readfile.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Sep 17, 2025

## [`readFile()`](functions-readfile.html "readFile\(\)")

The [`readFile()`](functions-readfile.html "readFile\(\)") function outputs the content of CSV lookup files or ad-hoc tables as events. This allows you to use a CSV [Lookup File](repositories-files-ui.html "Lookup Files") and ad-hoc table as data input. 

[`readFile()`](functions-readfile.html "readFile\(\)") can also be used to combine multiple CSV files and tables, regardless if the structure is identical. 

For more information about ad-hoc tables, see [Using Ad-hoc Tables](query-joins-methods-adhoc-tables.html "Using Ad-hoc Tables"). 

### Note

It is recommended to use the [`readFile()`](functions-readfile.html "readFile\(\)") function at the beginning of the query. Using the function later in the query will always discard anything before it, and only return the content of the files or tables. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`file`_](functions-readfile.html#query-functions-readfile-file)[a]| array of file/table names| required |  |  The name of the input files or input tables. In case of ad-hoc tables, you can alternatively use _`table`_ as an alias of the _`file`_ parameter.   
[_`include`_](functions-readfile.html#query-functions-readfile-include)|  array of strings| optional[b] |  |  Specifies the column names to read in the lookup file. If no argument is given, all columns are included.   
[_`limit`_](functions-readfile.html#query-functions-readfile-limit)|  number| optional[[b]](functions-readfile.html#ftn.table-functions-readfile-optparamfn) |  |  Limits the number of rows returned. Use `limit=N` to preview the first `N` rows of the files and tables. The files or tables will be outputted in the specified order, until the limit has been reached.   
|  | **Minimum**| `1`|   
[a] The parameter name [_`file`_](functions-readfile.html#query-functions-readfile-file) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`file`_](functions-readfile.html#query-functions-readfile-file) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     readFile("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     readFile(file="value")
> 
> These examples show basic structure only.

### [`readFile()`](functions-readfile.html "readFile\(\)") Function Operation

The [`readFile()`](functions-readfile.html "readFile\(\)") function requires one of these file or table sources to be available: 

  * An uploaded file (see [Upload lookup files](repositories-files-ui.html#repositories-files-ui-loading-files "Upload lookup files")). 

  * An ad-hoc table defined in the query. 

  * An installed package file. 




When using the [`readFile()`](functions-readfile.html "readFile\(\)") function, it will output each file or table as an event per row. The order of the output is as follows: 

  * The files or tables will be outputted in the order specified in the file or table parameter. 

  * For each file or table, the rows will be outputted as events in the order they are in the file or table. 




When reading a file from a package, the package name should be specified in addition to the filename. For example: 

logscale
    
    
    readFile("falcon/investigate/logoninfo.csv")

For more information on referring to package resources, see [Referencing Package Assets](https://library.humio.com/integrations/packages-asset-reference.html). 

If you are aiming to preview the content of large files, LogScale recommends always including the [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter to ensure optimal UI performance. However, when the file is utilized as data input for further manipulation, the [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter can be omitted. 

### [`readFile()`](functions-readfile.html "readFile\(\)") Examples

Click + next to an example below to get the full details.

#### Concatenate Multiple CSV Files

**Combine data from multiple CSV files into a single result set using the[`readFile()`](functions-readfile.html "readFile\(\)") function **

##### Query

logscale
    
    
    readFile("users_2024.csv", "users_2025.csv", "temp_users.csv")

##### Introduction

In this example, the [`readFile()`](functions-readfile.html "readFile\(\)") function is used to concatenate data from multiple CSV files named `users_2024.csv`, `users_2025.csv`, and `temp_users.csv`, combining all events into a single result set. 

Example data in the CSV files might look like this: 

File `users_2024.csv`: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
  
File `users_2025.csv`: 

user_id| name| department| join_date  
---|---|---|---  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
  
File `temp_users.csv`: 

user_id| name| department| join_date  
---|---|---|---  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         readFile("users_2024.csv", "users_2025.csv", "temp_users.csv")

Reads and concatenates data from three CSV files: `users_2024.csv`, `users_2025.csv`, and `temp_users.csv`. The [`readFile()`](functions-readfile.html "readFile\(\)") function processes each CSV file in the order specified and combines all events into a single result set, with events from the first file appearing first, followed by events from subsequent files. 

  3. Event Result set.




##### Summary and Results

The query is used to combine data from multiple CSV files into a single unified event set by concatenating their contents. 

This query is useful, for example, to merge data exports from different time periods, combine CSV files from multiple departments or regions, or consolidate data from various external sources for comprehensive analysis. 

Sample output from the incoming example data: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
Note that the CSV files could be different formats (field names and content), but typically the schemas would match which will make it easier to query and display in a widget. 

The events appear in the output in the same order as the files are specified in the function call, with all events from the first file appearing before any events from the second file, and so on. 

#### Concatenate Multiple Tables

**Combine data from multiple tables into a single result set using the[`readFile()`](functions-readfile.html "readFile\(\)") function **

##### Query

logscale
    
    
    readFile("users_2024", "users_2025", "temp_users")

##### Introduction

In this example, the [`readFile()`](functions-readfile.html "readFile\(\)") function is used to concatenate data from multiple lookup tables named `users_2024`, `users_2025`, and `temp_users`, combining all events into a single result set. 

Example data in the lookup tables might look like this: 

Table `users_2024`: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
  
Table `users_2025`: 

user_id| name| department| join_date  
---|---|---|---  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
  
Table `temp_users`: 

user_id| name| department| join_date  
---|---|---|---  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         readFile("users_2024", "users_2025", "temp_users")

Reads and concatenates data from three lookup tables: `users_2024`, `users_2025`, and `temp_users`. The [`readFile()`](functions-readfile.html "readFile\(\)") function processes each table in the order specified and combines all events into a single result set, with events from the first table appearing first, followed by events from subsequent tables. 

  3. Event Result set.




##### Summary and Results

The query is used to combine data from multiple lookup tables into a single unified event set by concatenating their contents. 

This query is useful, for example, to merge historical data stored in separate yearly tables, combine data from different regional databases, or consolidate temporary and permanent datasets for comprehensive analysis. 

Sample output from the incoming example data: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
Note that the tables could be different formats (field names and content), but typically the schemas would match which will make it easier to query and display in a widget. 

The events appear in the output in the same order as the files are specified in the function call, with all events from the first table appearing before any events from the second table, and so on. 

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

#### Preview And Output Several Lookup Files as Events With [`readFile()`](functions-readfile.html "readFile\(\)")

**Preview and output each .csv file as several events using the[`readFile()`](functions-readfile.html "readFile\(\)") function **

##### Query

logscale
    
    
    readFile(["file1.csv", "file2.csv"])

##### Introduction

In this example, the [`readFile()`](functions-readfile.html "readFile\(\)") function is used to preview and output several lookup files as events. The files will be outputted in the order specified in the file parameter. For each file, the rows will be outputted as events in the order they are in the file. 

Example incoming data from `file1.csv` might look like this: 

host_name| host_id  
---|---  
DESKTOP-VSKPBK8| 1  
FINANCE| 2  
homer-xubuntu| 3  
logger| 4  
  
Example incoming data from `file2.csv` might look like this: 

host_name| host_id  
---|---  
DESKTOP-1| 5  
DESKTOP-2| 6  
DESKTOP-3| 7  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         readFile(["file1.csv", "file2.csv"])

First outputs all the rows from `file1.csv` as events, then outputs all the rows from `file2.csv` as events. The rows maintain their original order. 

If you aim to preview the content of large files, __ls_shortname recommends always including the [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter to ensure optimal UI performance. For example: `readFile([file1.csv, file2.csv], limit=6)`. Note that the files will be outputted in the specified order, until the limit has been reached. If `file1.csv` has 4 rows and `file2.csv` has 3 rows, then the query will output all rows of `file1.csv` and 2 rows of `file2.csv`. 

If the files are utilized as data input for further manipulation, the [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter can be omitted. 

  3. Event Result set.




##### Summary and Results

The query is used to preview and output content in several CSV Lookup Files as events. The [`readFile()`](functions-readfile.html "readFile\(\)") function can also be used to read tables defined with the [`defineTable()`](functions-definetable.html "defineTable\(\)") function. 

Sample output from the incoming example data: 

host_id| host_name  
---|---  
1| DESKTOP-VSKPBK8  
2| FINANCE  
3| homer-xubuntu  
4| logger  
5| DESKTOP-1  
6| DESKTOP-2  
7| DESKTOP-3  
  
Sample output from the incoming example data with [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter: 

host_id| host_name  
---|---  
1| DESKTOP-VSKPBK8  
2| FINANCE  
3| homer-xubuntu  
4| logger  
5| DESKTOP-1  
6| DESKTOP-2  
  
#### Preview Content in a Lookup File With [`readFile()`](functions-readfile.html "readFile\(\)")

**Preview content in a lookup file in the search portion of a repo without having to match the lookup against data**

##### Query

logscale
    
    
    readFile("host_names.csv")

##### Introduction

In this example, the [`readFile()`](functions-readfile.html "readFile\(\)") function is used to look up a host_names.csv file just to preview the content in it. 

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

If you aim to preview the content of large files, we recommend always including the [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter to ensure optimal UI performance. For example: `readFile("host_names.csv", limit=5)`. However, if the file is utilized as data input for further manipulation, the [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter can be omitted. 

Notice that if reading a file from a package, then the package name should be specified in addition to the filename. For example: `readFile("falcon/investigate/logoninfo.csv")`. 

  3. Event Result set.




##### Summary and Results

The query is used to preview content in CSV Lookup Files. After previewing the content with the [`readFile()`](functions-readfile.html "readFile\(\)") function, it is possible to use the data for further manipulation, for example combine it with [`count()`](functions-count.html "count\(\)") to count the rows, [`select()`](functions-select.html "select\(\)") to filter data, [`join()`](functions-join.html "join\(\)") to match data, etc. 

The [`readFile()`](functions-readfile.html "readFile\(\)") function can also be used to read tables defined with the [`defineTable()`](functions-definetable.html "defineTable\(\)") function. See [Perform a Right Join Query to Combine Two Datasets](https://library.humio.com/examples/examples-define-table-right.html)

Sample output from the incoming example data: 

host_id| host_name  
---|---  
1| DESKTOP-VSKPBK8  
2| FINANCE  
3| homer-xubuntu  
4| logger  
5| DESKTOP-1  
6| DESKTOP-2  
7| DESKTOP-3  
  
Sample output from the incoming example data with [_`limit`_](functions-readfile.html#query-functions-readfile-limit) parameter: 

host_id| host_name  
---|---  
1| DESKTOP-VSKPBK8  
2| FINANCE  
3| homer-xubuntu  
4| logger  
5| DESKTOP-1  
  
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
