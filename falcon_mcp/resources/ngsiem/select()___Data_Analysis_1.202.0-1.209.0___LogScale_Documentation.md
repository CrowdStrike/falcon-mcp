# select() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-select.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`select()`](functions-select.html "select\(\)")

Specify a set of fields to select from each event and include in the resulting event set. 

It is possible that an aggregate function, such as [`table()`](functions-table.html "table\(\)") or [`groupBy()`](functions-groupby.html "groupBy\(\)") may be more suitable for summarizing and selecting the fields that you want to be displayed. 

A use-case for [`select()`](functions-select.html "select\(\)") is when you want to export a few fields from a large number of events into a CSV file without aggregating the values. Because an implicit [`tail(200)`](functions-tail.html "tail\(\)") function is appended in non-aggregating queries, only 200 events might be shown in those cases; however, when exporting the result, you get all matching events. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`fields`_](functions-select.html#query-functions-select-fields)[a]| array of strings| required |  |  The names of the fields to keep.   
[a] The parameter name [_`fields`_](functions-select.html#query-functions-select-fields) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`fields`_](functions-select.html#query-functions-select-fields) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     select(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     select(fields=["value"])
> 
> These examples show basic structure only.

### [`select()`](functions-select.html "select\(\)") Examples

Click + next to an example below to get the full details.

#### Reduce Large Event Sets to Essential Fields

**Reduce large datasets to essential fields using the[`select()`](functions-select.html "select\(\)") function **

##### Query

logscale
    
    
    method=GET
    select([statuscode, responsetime])

##### Introduction

The [`select()`](functions-select.html "select\(\)") function reduces large event set to essential fields. The [`select()`](functions-select.html "select\(\)") statement creates a table as default and copies data from one table to another. 

In this example, an unsorted table is selected for the statuscode field and the responsetime field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         method=GET

Filters for all HTTP request methods of the type `GET`. 

  3. logscale
         
         select([statuscode, responsetime])

Creates an unsorted table showing the statuscode field and the responsetime field. 

  4. Event Result set.




##### Summary and Results

The query is used to filter specific fields from an event set and create a table showing these fields (focused event set). In this example, the table shows the HTTP response status and the time taken to respond to the request which is useful for analyzing HTTP performance, monitoring response codes, and identifying slow requests.. The `select` function is useful when you want to export a few fields from a large number of events into a .CSV file without aggregating the values. For more information about export, see [Export Data](searching-data-data-export.html "Export Data"). 

Note that whereas the LogScale UI can only show up to 200 events, the exported .CSV file contains all results. 

It is possible that an aggregate function, such as [`table()`](functions-table.html "table\(\)") or [`groupBy()`](functions-groupby.html "groupBy\(\)") may be more suitable for summarizing and selecting the fields to be displayed. 

#### Select Fields to Export

**Select fields to export as .CSV file using the[`select()`](functions-select.html "select\(\)") function **

##### Query

logscale
    
    
    select([@timestamp, @rawstring])

##### Introduction

The [`select()`](functions-select.html "select\(\)") function reduces large event set to essential fields. The [`select()`](functions-select.html "select\(\)") statement creates a table as default and copies data from one table to another. 

In this example, an unsorted table is selected for the @timestamp field and the @rawstring field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         select([@timestamp, @rawstring])

Creates an unsorted table showing the @timestamp field and the @rawstring field. 

  3. Event Result set.




##### Summary and Results

The query is used to filter specific fields from an event set and create a table showing these fields (focused event set). In this example, the table shows the timestamp of the events and the complete raw log entry, which is useful for full log analysis, and data backup. The `select` function is useful when you want to export a few fields from a large number of events into a .CSV file without aggregating the values. For more information about export, see [Export Data](searching-data-data-export.html "Export Data"). 

Note that whereas the LogScale UI can only show up to 200 events, an exported .CSV file contains all results.
