# match() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-match.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`match()`](functions-match.html "match\(\)")

Matches or joins data from query results with a table. The table can be provided either as a lookup file — CSV file or through a limited form of JSON file, uploaded using [Lookup Files](repositories-files-ui.html "Lookup Files") — or as an ad-hoc table [Using Ad-hoc Tables](query-joins-methods-adhoc-tables.html "Using Ad-hoc Tables"). 

If you are looking for match expressions, see [Match Statements](syntax-conditional.html#syntax-conditional-match "Match Statements"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`column`_](functions-match.html#query-functions-match-column)|  string or array| optional[a] | `field parameter`|  Which column in the file to use for the match. A single column or an array of columns can be specified.   
[_`field`_](functions-match.html#query-functions-match-field)|  string or array| required |  |  Which field in the event (log line) must match the given column value. A single field or an array of fields can be specified. Field and column must have the same length, are matched in order and must all match.   
[_`file`_](functions-match.html#query-functions-match-file)[b]| string| required |  |  Specifies the source file (when using [Lookup Files](repositories-files-ui.html "Lookup Files")) or the name of the [ad-hoc table](query-joins-methods-adhoc-tables.html "Using Ad-hoc Tables"). The file name should be specified with a `.csv` or `.json` suffix. In case of ad-hoc tables, you can alternatively use _`table`_ as an alias of the _`file`_ parameter, for example `match(table="tablename", field=fieldname, column=name)`.   
[_`glob`_](functions-match.html#query-functions-match-glob) (deprecated)| boolean| optional[[a]](functions-match.html#ftn.table-functions-match-optparamfn) | `false`|  This parameter is deprecated. Use [_`mode`_](functions-match.html#query-functions-match-mode) parameter with the [`glob`](functions-match.html#query-functions-match-mode-option-glob) option instead. (**deprecated in 1.23**)  
[_`ignoreCase`_](functions-match.html#query-functions-match-ignorecase)|  boolean| optional[[a]](functions-match.html#ftn.table-functions-match-optparamfn) | [`false`](functions-match.html#query-functions-match-ignorecase-option-false)|  If true, ignore case when matching against the CSV data.   
|  |  | **Values**  
|  |  | [`false`](functions-match.html#query-functions-match-ignorecase-option-false)| Perform a case-sensitive match of the event values with the lookup table  
|  |  | [`true`](functions-match.html#query-functions-match-ignorecase-option-true)| Ignore the case of the event values with the lookup table  
[ _`include`_](functions-match.html#query-functions-match-include)|  string or array| optional[[a]](functions-match.html#ftn.table-functions-match-optparamfn) |  |  The columns to include. If no argument is given, include all columns from the corresponding row in the output event.   
[_`mode`_](functions-match.html#query-functions-match-mode)|  string| optional[[a]](functions-match.html#ftn.table-functions-match-optparamfn) | [`string`](functions-match.html#query-functions-match-mode-option-string)|  The function to use when matching against keys.   
|  |  | **Values**  
|  |  | [`cidr`](functions-match.html#query-functions-match-mode-option-cidr)| The key is interpreted as a CIDR subnet and the event is matched if the field contains an IP within the subnet. If multiple subnets match, the most specific one is selected or an arbitrary one if there are multiple equally specific subnets.  
|  |  | [`glob`](functions-match.html#query-functions-match-mode-option-glob)| The key is interpreted as a globbing pattern with `*` appended to the beginning and end of the supplied string, and matched accordingly. For example, a CSV key value of `thisMatch` would match the field value of `123thisMatch456`. When using [_`mode=glob`_](functions-match.html#query-functions-match-mode), the underlying CSV is limited to 20,000 rows/lines.  For self-hosted customers, the maximum value for glob matches is configurable using [`GLOB_MATCH_LIMIT`](https://library.humio.com/falcon-logscale-self-hosted/envar-glob_match_limit.html).   
|  |  | [`string`](functions-match.html#query-functions-match-mode-option-string)| The matching is done using exact string matching.  
|  | **Controlling Variables**  
|  | [`GLOB_MATCH_LIMIT`](https://library.humio.com/falcon-logscale-self-hosted/envar-glob_match_limit.html)|  **Variable default:** 20,000  
[ _`nrows`_](functions-match.html#query-functions-match-nrows)|  string| optional[[a]](functions-match.html#ftn.table-functions-match-optparamfn) | `1`|  The maximum number of rows an event can match with in a CSV file.   
|  |  | **Values**  
|  |  | [`max`](functions-match.html#query-functions-match-nrows-option-max)| Use the maximum number of matches  
|  | **Maximum**| [`500`](functions-match.html#query-functions-match-nrows-max-500)|   
[ _`strict`_](functions-match.html#query-functions-match-strict)|  boolean| optional[[a]](functions-match.html#ftn.table-functions-match-optparamfn) | `true`|  If `true` (the default) selects only the events that match a key in the file; if `false` lets all events through (works like the deprecated [`lookup()`](https://library.humio.com/data-analysis-1.70/functions-lookup.html)).   
[_`nrows`_](functions-match.html#query-functions-match-nrows)|  string| required | [`10`](functions-match.html#query-functions-match-nrows-max-10)|  The maximum number of rows an event can match with in a CSV file. In case of more matches than _`nrows`_ , the latest _`nrows`_ are selected.   
|  | **Maximum**| [`10`](functions-match.html#query-functions-match-nrows-max-10)|   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`file`_](functions-match.html#query-functions-match-file) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`file`_](functions-match.html#query-functions-match-file) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     match("value",nrows=10,field="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     match(file="value",nrows=10,field="value")
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
>     !match()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not match()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`match()`](functions-match.html "match\(\)") Function Operation

The [`match()`](functions-match.html "match\(\)") function has specific implementation and operational considerations, outlined below. 

  * When lookup information from files are loaded from a package, the package name should be specified in addition to the filename. For example: 

logscale
        
        match("falcon/investigate/logoninfo.csv",field="loookupname")

For more information on referring to package resources, see [Referencing Package Assets](https://library.humio.com/integrations/packages-asset-reference.html). 

  * The default behavior of this function — when [_`strict`_](functions-match.html#query-functions-match-strict) is set to `true` — works like an `INNER JOIN`. When [_`strict`_](functions-match.html#query-functions-match-strict) is set to `false` the function enriches events. 

  * When using [_`mode=glob`_](functions-match.html#query-functions-match-mode), the underlying CSV is limited to 20,000 rows/lines. 

  * For self-hosted customers, the maximum value for glob matches is configurable using [`GLOB_MATCH_LIMIT`](https://library.humio.com/falcon-logscale-self-hosted/envar-glob_match_limit.html). 

  * When using [_`mode=glob`_](functions-match.html#query-functions-match-mode), the match will order the matches according to their Unicode (or lexicographical) order when there are multiple matches. 




### Using [`match()`](functions-match.html "match\(\)") with Ad-hoc Tables

[`match()`](functions-match.html "match\(\)") can be used to perform a join using ad-hoc tables. See [Using Ad-hoc Tables](query-joins-methods-adhoc-tables.html "Using Ad-hoc Tables") for more information. 

### Using [`match()`](functions-match.html "match\(\)") with Lookup Files

When using [`match()`](functions-match.html "match\(\)") for joining with [Lookup Files](repositories-files-ui.html "Lookup Files"), two file formats are supported: 

  * CSV. The recommended format, ensures better performance, allows for additional functionalities (using parameters) and is compatible with related functions, like [`readFile()`](functions-readfile.html "readFile\(\)"). See [CSV File Formats](functions-match.html#functions-match-files-csv "CSV File Formats") for more information. 

  * JSON. Supports object and array-based formats. See [JSON File Formats](functions-match.html#functions-match-files-json "JSON File Formats") for more information. 




#### CSV File Formats

For Comma Separated Values (CSV) files, whitespace gets included in the keys and values. To include the comma separator `,` in a value, quote using the `"` character. The following file is a valid CSV file: 

csv
    
    
    userid,name
    1,chr
    2,krab
    "4","p,m"
    7,mgr

The first line is interpreted as the column title. When querying, the column in the field should be used to identify which column to match against. 

When using [`match()`](functions-match.html "match\(\)") with a single column: 

logscale
    
    
    match(test.csv, field=somefield, column=column1)

the last matching row in `test.csv` is used. 

Since the function supports the selection of an array of columns, you can match multiple pairs of fields and columns against a CSV file. For example, with these events and fields: 

json
    
    
    {
      field1: c,
      field2: f
    },
    {
      field1: c,
      field2: e
    }

and the following `test.csv` match file: 

csv
    
    
    column1, column2, column3
    a,        b,      d
    c,        d,      a
    c,        e,      f

The example query: 

logscale
    
    
    match(test.csv, field=[field1, field2], column=[column1, column2])

will produce the following output: 

item| value  
---|---  
field1| c  
field2| e  
column3| f  
  
Similar to when matching against a single column, in the case of multiple columns, the function will use the **last** matching row in the file. This behavior is applied starting from version 1.145. 

[`match()`](functions-match.html "match\(\)") supports matching on multiple rows, meaning that you can match a single event with multiple rows. Each matching row will generate a separate event. 

**Example 1** with `nrows=2`. With event: 

json
    
    
    {
      field1: c
    }

and the following `test.csv` match file: 

csv
    
    
    column1, column2, column3
    c,        b,      a
    a,        b,      d
    c,        d,      a
    c,        e,      f

The example query: 

logscale
    
    
    match(test.csv, field=field1, column=column1, nrows=2)

will generate the following output: 

item| value  
---|---  
field1| c  
column2| e  
column3| f  
field1| c  
column2| d  
column3| a  
  
**Example 2** with `nrows=max`. With event: 

json
    
    
    {
      field1: c
    }

and the following `test.csv` match file: 

csv
    
    
    column1, column2, column3
    c,        b,      a
    a,        b,      d
    c,        d,      a
    c,        e,      f

The example query: 

logscale
    
    
    match(some.csv, field=field1, column=column1, nrows=max)

will generate the following output: 

item| value  
---|---  
field1| c  
column2| e  
column3| f  
field1| c  
column2| d  
column3| a  
field1| c  
column2| b  
column3| a  
  
**Example 3** with `nrows=2`. Given weblog data, HTTP methods could be matched to multiple rows for the type of output: 

logscale
    
    
    method=POST
    | match(file="methods.csv",nrows=2,field=method,column="method")

The following `methods.csv` match file: 

csv
    
    
    method,description
    POST,Send Data
    POST,Transfer Data in
    GET,Retrieve Data
    GET,Get Data

could be matched with a longer description, showing two different rows for each matching source row: 

method| description| url  
---|---|---  
POST| Send Data| /humio/api/v1/ingest/elastic-bulk  
POST| Transfer Data in| /humio/api/v1/ingest/elastic-bulk  
POST| Transfer Data in| /humio/api/v1/ingest/elastic-bulk  
POST| Send Data| /humio/api/v1/ingest/elastic-bulk  
POST| Transfer Data in| /humio/api/v1/ingest/elastic-bulk  
POST| Send Data| /humio/api/v1/ingest/elastic-bulk  
  
When matching multiple rows, multiple events, matching the number of matched [_`nrows`_](functions-match.html#query-functions-match-nrows), will be generated for each corresponding event and matched lookup entry. 

#### JSON File Formats

For JSON files, two formats are supported: 

  * Object-based, where the lookup field does not have an explicit name 

  * Array-based, where the information is an array of objects 




In the Object-based variant, the lookup values are declared as an object with a key and embedded fields, the key field does not have a name. 

json
    
    
    {
      "1": { "name": "chr" },
      "2": { "name": "krab" },
      "4": { "name": "pmm" },
      "7": { "name": "mgr" }
    }

### Important

Nested JSON objects are not supported. Uploading a file with nested objects will not fail, but the information cannot be matched. 

When matching against a file in this case, the name of the field in the JSON object does not need to be used; the key for each value is used instead. For example: 

logscale
    
    
    groupBy(@timezone)
    | count(@timezone)
    | match(file="short.json",field=_count)

In the above, the value of _count will be matched, outputting the match value: 

_count| name  
---|---  
2| krab  
  
In the array-based variant, the lookup values are declared as an array of objects, you select which field is the key using the [_`field`_](functions-match.html#query-functions-match-field) parameter in [`match()`](functions-match.html "match\(\)"). 

json
    
    
    [
      { "userid": "1", "name": "chr" },
      { "userid": "2", "name": "krab" },
      { "userid": "4", "name": "pmm" },
      { "userid": "7", "name": "mgr" }
    ]

When using this version, the name of the column to be matched must be specified using the [_`column`_](functions-match.html#query-functions-match-column) argument to [`match()`](functions-match.html "match\(\)"): 

logscale
    
    
    groupBy(@timezone)
    | count(@timezone)
    | match(file="long.json",field=_count,column="userid")

This behavior also means that any field in the JSON file can be used as the match value. For example: 

logscale Syntax
    
    
    ...
    | match(file="long.json",field=codename,column="name")

This can be useful if you have a JSON file that contains multiple possible lookup values for given records. 

For 

### Important

The [`match()`](functions-match.html "match\(\)") function does not report an error if the file format cannot be parsed. 

#### Parser Behavior with Missing or Invalid Files

When using [`match()`](functions-match.html "match\(\)") in parser queries that reference an uploaded lookup file, the function may encounter missing or invalid files, if for example they're temporary unavailable. In such cases, the parser continues processing data normally but generates a warning message. See [Parser Warning](parsers-create.html#parser-warning) for more information. 

### [`match()`](functions-match.html "match\(\)") Examples

Click + next to an example below to get the full details.

####  Match Multiple Pairs of Event Fields Against Multiple Columns in .CSV Lookup File

**Compare multiple pairs of event fields against multiple columns in a .CSV lookup file using the[`match()`](functions-match.html "match\(\)") function **

##### Query

logscale
    
    
    match(test.csv, field=[field1, field2], column=[column1, column2])

##### Introduction

In this example, the [`match()`](functions-match.html "match\(\)") function is used to match multiple pairs of fields against multiple columns in a CSV file named `test.csv` simultaneously. 

Example incoming event data might look like this: 

json
    
    
    [
       {
          "field1" : "c",
          "field2" : "f"
       },
       {
          "field2" : "e",
          "field1" : "c"
       }
    ]

Example `test.csv` file data might look like this: 

column1| column2| column3  
---|---|---  
a| b| d  
c| d| a  
c| e| f  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         match(test.csv, field=[field1, field2], column=[column1, column2])

For each event, checks if field1 matches column1 and field2 matches column2

  3. Event Result set.




##### Summary and Results

The query is used to match multiple pairs of event fields against multiple columns in the .CSV file named `test.csv`. Multiple field matching helps validate and enrich complex event data. 

Sample output from the incoming example data: 

column3| field1| field2  
---|---|---  
f| c| e  
  
#### Filter For Items Not Part of Data Set Using `!match()`

**Find the set difference using the[`match()`](functions-match.html "match\(\)") function with negation **

##### Query

logscale
    
    
    src_ip=*
    | !match("known_ips.csv", field=src_ip)

##### Introduction

In this example, the [`match()`](functions-match.html "match\(\)") function is used with a negation to search and find IP addresses, that are not part of a known list `known_ips.csv`. 

![](images/venn-seta-not-setb.png)  
---  
  
Example incoming data might look like this: 

timestamp| src_ip| dst_ip| src_port| dst_port| protocol| bytes_sent| bytes_received  
---|---|---|---|---|---|---|---  
2025-04-01T07:00:00Z| 192.168.1.101| 10.0.0.50| 52431| 443| TCP| 1024| 2048  
2025-04-01T07:00:01Z| 172.16.0.24| 8.8.8.8| 33221| 53| UDP| 64| 512  
2025-04-01T07:00:02Z| 192.168.1.150| 172.16.0.100| 49223| 80| TCP| 2048| 4096  
2025-04-01T07:00:03Z| 10.0.0.75| 192.168.1.1| 55678| 22| TCP| 512| 1024  
2025-04-01T07:00:04Z| 192.168.1.200| 1.1.1.1| 44556| 53| UDP| 64| 512  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         src_ip=*

Filters for all events that have a src_ip field. 

  3. logscale
         
         | !match("known_ips.csv", field=src_ip)

Excludes (filters out) any events where the src_ip field matches entries in the file `known_ips.csv`, and returns a list of IP addresses that are not found in the specified file. The negation operator is used to return non-matching results. 

  4. Event Result set.




##### Summary and Results

The query is used to search for unknown or unexpected source IP addresses matched up againt a known list. This is useful for detecting potential security theats and monitoring for unauthorized network access. 

Sample output from the incoming example data: 

timestamp| src_ip| dst_ip| src_port| dst_port| protocol| bytes_sent| bytes_received  
---|---|---|---|---|---|---|---  
2025-04-01T07:00:00Z| 192.168.1.101| 10.0.0.50| 52431| 443| TCP| 1024| 2048  
2025-04-01T07:00:01Z| 172.16.0.24| 8.8.8.8| 33221| 53| UDP| 64| 512  
  
#### Match Event Fields Against Lookup Table Values

**Compare event fields with column values in a lookup table using the[`match()`](functions-match.html "match\(\)") function **

##### Query

logscale
    
    
    match(file="users.csv", column=userid, field=id, include=[])

##### Introduction

In this example, the [`match()`](functions-match.html "match\(\)") function is used to match the column userid of the `users.csv` file against the id field in the event. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         match(file="users.csv", column=userid, field=id, include=[])

Matches events for which the id field matches the value of the column userid in the `users.csv` file (the lookup table file). All events with non-matching IDs are filtered out. 

No additional columns are added. 

  3. Event Result set.




##### Summary and Results

The query is used to compare and match event fields and file values as strings, in this case using exact string matching (the default value of the [_`mode`_](functions-match.html#query-functions-match-mode) parameter is `string`). The [`match()`](functions-match.html "match\(\)") function is useful for comparing or combining data from multiple sources. In this example, only events with matching values are passed on, meaning that all events with non-matching IDs are removed. Matching events against an authorized users list is, for example, useful for filtering out unauthorized access attempts, for validation of user activities, or other monitoring. 

#### Match Event Fields Against Lookup Table Values Adding Specific Columns

**Compare event IP fields with CIDR ranges in lookup table using the[`match()`](functions-match.html "match\(\)") function with [_`mode`_](functions-match.html#query-functions-match-mode) parameter **

##### Query

logscale
    
    
    match(file="cidr-file.csv", column="cidr-block", field=ip, mode=cidr, include=["info","type"])

##### Introduction

In this example, the [`match()`](functions-match.html "match\(\)") function is used to match event IP addresses against the column cidr-block of the `cidr-file.csv` file, adding specific columns details to the events. 

The query matches IP addresses against CIDR blocks (CIDR subnets) and adds specific network information from the columns info and type to the output rows. 

Example incoming event data might look like this: 

@timestamp| ip| action  
---|---|---  
2024-01-15T09:00:00.000Z| 10.0.1.25| login  
2024-01-15T09:01:00.000Z| 192.168.1.100| connect  
2024-01-15T09:02:00.000Z| 172.16.5.12| access  
  
Example `cidr-file.csv` file data might look like this: 

cidr-block| info| type| location| department  
---|---|---|---|---  
10.0.1.0/24| Internal Network| corporate| HQ| IT  
192.168.1.0/24| Development Network| test| Lab| Engineering  
172.16.0.0/16| Production Network| critical| DC| Operations  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         match(file="cidr-file.csv", column="cidr-block", field=ip, mode=cidr, include=["info","type"])

Uses CIDR ranges matching to match the cidr-block column of the `cidr-file.csv` lookup table file against the IP addresses (ip field) in the events, and adds specific network information to the output rows. 

It will only add the specified columns of the matching row. The column names become new field names. 

Note that when the [_`mode`_](functions-match.html#query-functions-match-mode) parameter is set to `cidr`, then the event is matched if the field contains an IP address within the CIDR subnet. If multiple subnets match, the most specific one is selected, or an arbitrary one, if there are multiple equally specific subnets. 

  3. Event Result set.




##### Summary and Results

The query is used to match IP addresses against CIDR blocks and add specific network information from the columns info and type to the output rows. 

The query helps analyze network traffic and security events by mapping IP addresses to network segments. 

Sample output from the incoming example data: 

@timestamp| ip| action| info| type  
---|---|---|---|---  
2024-01-15T09:00:00.000Z| 10.0.1.25| login| Internal Network| corporate  
2024-01-15T09:01:00.000Z| 192.168.1.100| connect| Development Network| test  
2024-01-15T09:02:00.000Z| 172.16.5.12| access| Production Network| critical  
  
Note how only the specified fields from the ` cidr-file.csv` file appear in output. 

#### Match Event Fields Against Lookup Table Values Allowing All Events to Pass

**Compare event fields with column values in lookup table using the[`match()`](functions-match.html "match\(\)") function with [_`strict`_](functions-match.html#query-functions-match-strict) parameter to allow also non-matching events to pass **

##### Query

logscale
    
    
    id =~ match(file="users.csv", column=userid, strict=false)

##### Introduction

In this example, the [`match()`](functions-match.html "match\(\)") function is used to match event IDs against the column userid of the `users.csv` file, adding the matching user details to the events. As the [_`strict`_](functions-match.html#query-functions-match-strict) parameter is set to `true`, all events - including non-matching events - are passed through, but only events with matches will be enriched with all other columns of the matching row. 

Example incoming event data might look like this: 

@timestamp| id| action| source_ip  
---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1  
2024-01-15T09:01:00.000Z| unknown-user| login_attempt| 10.0.0.2  
2024-01-15T09:02:00.000Z| dev-user-456| code_push| 10.0.0.3  
  
Example `users.csv` file data might look like this: 

userid| department| access_level| location  
---|---|---|---  
ADMIN-123| IT| administrator| HQ  
dev-user-456| Engineering| developer| Remote  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         id =~ match(file="users.csv", column=userid, strict=false)

When an event ID matches the column userid in the `users.csv` lookup file, all columns from that first matching row are added to the event. The column names become new field names. 

As the [_`strict`_](functions-match.html#query-functions-match-strict) parameter is set to `true`, all events - including non-matching events - are passed through, but only events with matches will be enriched with all other columns of the matching row. 

  3. Event Result set.




##### Summary and Results

The query is used to enrich matching events while allowing all events to pass through. Matching events against an authorized users list is, for example, useful for filtering out unauthorized access attempts, for validation of user activities, or other monitoring. Showing non-matching events in output as well can, for example, be useful for tracking unauthorized access attempts, identifying unknown users or systems or for monitoring suspicious activities. 

Sample output from the incoming example data: 

@timestamp| id| action| source_ip| department| access_level| location  
---|---|---|---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1| IT| administrator| HQ  
2024-01-15T09:01:00.000Z| unknown-user| login_attempt| 10.0.0.2| <no value>| <no value>| <no value>  
2024-01-15T09:02:00.000Z| dev-user-456| code_push| 10.0.0.3| Engineering| developer| Remote  
  
After matching, the output combines original event fields with matched user details. Note how also non-matching events (in this example `unknown-user`) appear in output. 

#### Match Event Fields Against Patterns in Lookup Table Values

**Compare event fields with column values containing patterns in a lookup table using the[`match()`](functions-match.html "match\(\)") function with glob pattern matching **

##### Query

logscale
    
    
    id =~ match(file="users.csv", column=userid, mode=glob, ignoreCase=true)

##### Introduction

In this example, the [`match()`](functions-match.html "match\(\)") function is used with glob pattern matching (defined by the [_`mode`_](functions-match.html#query-functions-match-mode) parameter) to match event IDs against the column userid of the `users.csv` file, adding the matching user details to the events. 

Example incoming event data might look like this: 

@timestamp| id| action| source_ip  
---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1  
2024-01-15T09:01:00.000Z| dev-user-456| code_push| 10.0.0.2  
2024-01-15T09:02:00.000Z| TEST_789| test_run| 10.0.0.3  
2024-01-15T09:03:00.000Z| support-001| ticket_update| 10.0.0.4  
2024-01-15T09:04:00.000Z| unknown-user| login_attempt| 10.0.0.5  
  
Example `users.csv` file data might look like this: 

userid| department| access_level| location| title  
---|---|---|---|---  
ADMIN-*| IT| administrator| HQ| System Administrator  
dev-user-*| Engineering| developer| Remote| Software Engineer  
TEST_*| QA| tester| Lab| QA Engineer  
support-*| Support| agent| Office| Support Specialist  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         id =~ match(file="users.csv", column=userid, mode=glob, ignoreCase=true)

Uses glob pattern matching to match the userid column of the `users.csv` lookup table file against the IDs in the events. When an event ID matches a pattern in `users.csv`, all (non-pattern) columns from that first matching row are added to the event. The column names become new field names. 

Pattern matching examples based on the input data and lookup file are: 

`ADMIN-123` matches `ADMIN-*`

`dev-user-456` matches `dev-user-*`

`TEST_789` matches `TEST_*`

`support-001` matches `support-*`

  3. Event Result set.




##### Summary and Results

The query is used to match event IDs against patterns in a user list, and then add the matching user details (other columns from the row in the `users.csv` file) to the events. 

Pattern-based matching with field enrichment is, for example, useful in case you want to add user context to authentication logs. 

Sample output from the incoming example data: 

@timestamp| id| action| source_ip| department| access_level| location| title  
---|---|---|---|---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1| IT| administrator| HQ| System Administrator  
2024-01-15T09:01:00.000Z| dev-user-456| code_push| 10.0.0.2| Engineering| developer| Remote| Software Engineer  
2024-01-15T09:02:00.000Z| TEST_789| test_run| 10.0.0.3| QA| tester| Lab| QA Engineer  
2024-01-15T09:03:00.000Z| support-001| ticket_update| 10.0.0.4| Support| agent| Office| Support Specialist  
  
After matching, the output combines original event fields with matched user details. Only events with matching patterns appear in output.
