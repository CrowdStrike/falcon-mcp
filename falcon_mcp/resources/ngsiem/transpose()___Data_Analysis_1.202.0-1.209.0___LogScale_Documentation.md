# transpose() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-transpose.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`transpose()`](functions-transpose.html "transpose\(\)")

Transposes (transforms) table data by converting columns into rows, switching the orientation. This is a great way of reorganizing data into a more readable format or a format that can be more easily applied to other display formats as part of a widget. Use [`transpose()`](functions-transpose.html "transpose\(\)") to transpose a (table-like) query result by creating an event (row) for each column (attribute name), in which attributes are named `row[1]`, `row[2]`, etc. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`column`_](functions-transpose.html#query-functions-transpose-column)|  string| optional[a] | `column`|  Field to use as column value.   
[_`header`_](functions-transpose.html#query-functions-transpose-header)|  string| optional[[a]](functions-transpose.html#ftn.table-functions-transpose-optparamfn) |  |  Field to use as header value.   
[_`limit`_](functions-transpose.html#query-functions-transpose-limit)|  integer| optional[[a]](functions-transpose.html#ftn.table-functions-transpose-optparamfn) | `5`|  Maximum number of rows to transpose.   
|  | **Minimum**| `1`|   
|  | **Maximum**| `1,000`|   
[ _`pivot`_](functions-transpose.html#query-functions-transpose-pivot)[b]| string| optional[[a]](functions-transpose.html#ftn.table-functions-transpose-optparamfn) |  |  Field to use as both header AND column value.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`pivot`_](functions-transpose.html#query-functions-transpose-pivot) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`pivot`_](functions-transpose.html#query-functions-transpose-pivot) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     transpose("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     transpose(pivot="value")
> 
> These examples show basic structure only.

### [`transpose()`](functions-transpose.html "transpose\(\)") Function Operation

For example, given a query that returns a table, such as: 

logscale
    
    
    groupBy(loglevel)

loglevel |  _count   
---|---  
ERROR |  2   
WARN |  400   
INFO |  200   
  
The result can be transposed to: 

logscale
    
    
    groupBy(loglevel)
    | transpose()

column |  row[1] |  row[2] |  row[3]   
---|---|---|---  
_count |  2 |  400 |  200   
loglevel |  ERROR |  WARN |  INFO   
  
To use the loglevel row as the header, use: 

logscale Syntax
    
    
    ...
    | transpose(header=loglevel)

column |  ERROR |  WARN |  INFO   
---|---|---|---  
_count |  2 |  400 |  200   
  
### [`transpose()`](functions-transpose.html "transpose\(\)") Examples

Click + next to an example below to get the full details.

#### Create a Pivot Table

**Creating a view of LogScale activity**

##### Query

logscale
    
    
    groupBy([type,actor.user.id],function={groupBy(actor.user.id, function=max(@timestamp))})
    |transpose(header=type)
    |drop(column)

##### Introduction

The [humio-audit](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-audit.html) repository contains audit events for the LogScale cluster. Reporting on this information can provide a wealth of information, but a useful summary can be created based on the activities, users and which the latest user of that particular operation. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy([type,actor.user.id],function={groupBy(actor.user.id, function=max(@timestamp))})

The first step to creating a pivot table is the base query that will create the initial summary of the information. In this fragment, a nested [`groupBy()`](functions-groupby.html "groupBy\(\)") aggregation. The embedded aggregation creates a group of the maximum access time for a given user, by using [`max()`](functions-max.html "max\(\)") on the @timestamp against the actor.user.id. This creates a table of the last event by the user. The outer [`groupBy()`](functions-groupby.html "groupBy\(\)") then creates an aggregation of this maximum user time against the type which defines the operation performed. 

The result is a table of the last user and time for a specific operation; for example, the last time a query was executed. An example of this table can be seen below: 

type |  actor.user.id |  _max  
---|---|---  
`alert.clear-error` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700546666592   
`alert.create` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1699004139419   
`alert.update` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700546666676   
`dashboard.create` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1698417330709   
`dataspace.query` |  `0O7WGPBX9YbvZbKOrBMd5fgH` |  1700721296197   
  
  3. logscale
         
         |transpose(header=type)

The [`transpose()`](functions-transpose.html "transpose\(\)") will convert individual columns into rows, switching the orientation. For example, the type column will now become the type row. However, there are no row titles, so the title for the resulting table will by default create a header row containing the column and row numbers, like this: 

column |  row[1] |  row[2] |  row[3] |  row[4] |  row[5]  
---|---|---|---|---|---  
_max |  1700546666592 |  1699004139419 |  1700546666676 |  1698417330709 |  1700722209214   
actor.user.id |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
type |  alert.clear-error |  alert.create |  alert.update |  dashboard.create |  dataspace.query   
  
However, the aggregate grouping, type could be used instead as a valid header for each column. To achieve that, use the [_`header`_](functions-transpose.html#query-functions-transpose-header) parameter to specify type as the column. The resulting table now looks like this: 

alert.clear-error |  alert.create |  alert.update |  column |  dashboard.create |  dataspace.query  
---|---|---|---|---|---  
1700546666592 |  1699004139419 |  1700546666676 |  _max |  1698417330709 |  1700722210073   
0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  actor.user.id |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
  
  4. logscale
         
         |drop(column)

The table created contains the summarized information pivoted around the user ID and last event time further summarized by the type of the event. However, there is a column in the table, column, which is now a field in the event stream that was generated from the old row before the table was pivoted. 

That column can be removed by dropping the column field from the event using [`drop()`](functions-drop.html "drop\(\)") to remove the column from the events. 

  5. Event Result set.




##### Summary and Results

Pivoting an event set of data allows for the information to be displayed and summarized in a format that may make more logical sense as a display format. The final table will look like this: 

alert.clear-error |  alert.create |  alert.update |  dashboard.create |  dataspace.query   
---|---|---|---|---  
1700546666592 |  1699004139419 |  1700546666676 |  1698417330709 |  1700722210073   
0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH |  0O7WGPBX9YbvZbKOrBMd5fgH   
  
#### Search Accross Multiple Structured Fields

**Search across multiple structured fields using the transpose() function within groupBy()**

##### Query

logscale
    
    
    groupBy(@id, function=transpose())
    | row[1] = /httpd/
    | groupBy(column)

##### Introduction

By transposing event set, the information can be viewed and summarized in a more human readable form. In this example, the [`transpose()`](functions-transpose.html "transpose\(\)") function is used within a [`groupBy()`](functions-groupby.html "groupBy\(\)") function to search across multiple structured fields in the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository. 

Example incoming data might look like this: 

host| @rawstring  
---|---  
MAIL01| 2025-03-18T10:14:47.142Z MAIL01 httpd[61789]: 192.168.0.198 - - [2025-03-13:23:05:48 +0800] "GET /api/v2/products/search HTTP/1.1" 200 33456  
LON-SRV01| 2025-03-18T10:14:46.940Z LON-SRV01 httpd[60123]: 192.168.0.198 - - [2025-03-13:20:50:14 +0500] "GET /uploads/documents/terms.pdf HTTP/1.1" 401 36912  
MAIL01| 2025-03-18T10:14:46.691Z MAIL01 httpd[51234]: 192.168.0.198 - - [2025-03-13:12:50:16 -0300] "GET /downloads/mobile/app-v2.1.apk HTTP/1.1" 403 1234  
SYD-SRV01| 2025-03-18T10:14:46.542Z SYD-SRV01 httpd[45678]: 192.168.1.123 - - [2025-03-13:19:30:17 +0400] "GET /uploads/avatars/default.png HTTP/1.1" 404 61789  
PROD-SQL01| 2025-03-18T10:14:46.141Z PROD-SQL01 httpd[56789]: 192.168.1.245 - - [2025-03-13:17:30:38 +0200] "GET /uploads/avatars/default.png HTTP/1.1" 200 13456  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(@id, function=transpose())

Groups events by unique @id values, applies the [`transpose()`](functions-transpose.html "transpose\(\)") function for each group, converting row values into column headers. A new row-based structure for each @id field is created. 

After using [`transpose()`](functions-transpose.html "transpose\(\)"), the data might look like this: 

@id| column| row[1]  
---|---|---  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| @timezone| Z  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| app| httpd[56789]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| host| PROD-SQL01  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886,msg, 192.168.1.245 - - [2025-03-13:17:30:38 +0200] "GET /uploads/avatars/default.png HTTP/1.1" 200 13456|  |   
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| priority| 34  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| version| 1  
  
  3. logscale
         
         | row[1] = /httpd/

Filters for events where row[1] regex matches the value `httpd`. 

After filtering, the data might look like this (@rawstring has been removed from the below for clarity): 

@id| column| row[1]  
---|---|---  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_520_1742292886| app| httpd[56789]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_528_1742292886| app| httpd[45678]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_531_1742292886| app| httpd[51234]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_536_1742292886| app| httpd[60123]:  
xhCUZ4fQzxEbr3qoyzLIQqSE_0_540_1742292887| app| httpd[61789]:  
  
  4. logscale
         
         | groupBy(column)

Groups results by the column field, showing which original fields contained the value `httpd`, and makes a count of matches per field, returning the counted results in a field named _count. The final groupBy(column) removes duplicate entries. 

  5. Event Result set.




##### Summary and Results

The query is used to search across multiple structured fields in the [HUMIO](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository to show where `httpd` appears most often. It makes results more readable, identifies field patterns, and is very useful for statistical analysis. 

Sample output from the incoming example data: 

column| _count  
---|---  
@rawstring| 5  
app| 5  
  
#### Transpose a Basic Table

**Transposing an event set effectively switches rows (each event) into columns (an event)**

##### Query

logscale
    
    
    groupBy([loglevel])
    | transpose(header=loglevel)
    | drop(column)

##### Introduction

By transposing event set, the information can be viewed and summarized in a more human readable form. Transposing also allows for aggregated data to be viewed in a form where the value of an aggregated field becomes the columns. This can be used to summarize the information further by showing multiple rows of data. For example, in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository the event information contains a list of errors, warnings, or informational events for activity within the cluster. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy([loglevel])

Aggregates the lows by the loglevel. This field will either be `WARN`, `ERROR` or `INFO` depending on the level of the event log entry. The default function is used, which results in a count in the number of times an event of this type has been seen: 

loglevel |  _count  
---|---  
`ERROR` |  27424   
`INFO` |  18840156   
`WARN` |  2059898   
  
In this output, each event is a row in the table, each with two fields, loglevel and _count. 

  3. logscale
         
         | transpose(header=loglevel)

Transposing the events within the [`transpose()`](functions-transpose.html "transpose\(\)") will make each field in each event a row in the new stream of events, for example, the loglevel field with the value `ERROR` will become the field ERROR, swapping the rows for columns. By using the [_`header`_](functions-transpose.html#query-functions-transpose-header) parameter, [`transpose()`](functions-transpose.html "transpose\(\)") uses the value of the aggregated field as the fieldname. The output will now be a table with a column (field) for each value, and a single row with the count: 

ERROR |  INFO |  WARN |  column  
---|---|---|---  
97159 |  63719404 |  5716733 |  _count   
  
  4. logscale
         
         | drop(column)

In the final output, the column field in the events is the one generated from the field names of the original events and it's not needed, so it can be removed by using the [`drop()`](functions-drop.html "drop\(\)") function to remove the field from the event set. 

  5. Event Result set.




##### Summary and Results

The [`transpose()`](functions-transpose.html "transpose\(\)") is a great way of reorganizing data into a format is either more readable, or easily applied to other display formats as part of a widget. The final table looks like this: 

ERROR |  INFO |  WARN  
---|---|---  
97159 |  63719404 |  5716733   
  
However, the information as it is now formatted can more easily be applied to a variety of visualizations. For example, the data can be formatted as a bar chart, as we now have a list of fields and a value: 

![](images/functions/examples/transpose/transpose-basic-bar.png)  
---  
  
The difference is that without [`transpose()`](functions-transpose.html "transpose\(\)"), the aggregate result set is a list of events with a field name and value. With [`transpose()`](functions-transpose.html "transpose\(\)"), the result set is a single event with multiple fields, and this is interpreted by the bar chart as a series of values.
