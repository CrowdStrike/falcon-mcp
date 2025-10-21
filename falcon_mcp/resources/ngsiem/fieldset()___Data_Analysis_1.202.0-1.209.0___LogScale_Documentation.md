# fieldset() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-fieldset.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`fieldset()`](functions-fieldset.html "fieldset\(\)")

Retrieves a list of available fields. 

### Note

This function takes no parameters. 

### [`fieldset()`](functions-fieldset.html "fieldset\(\)") Examples

Click + next to an example below to get the full details.

#### Request List of Fields

**Request a list of all fields in a repository using the[`fieldset()`](functions-fieldset.html "fieldset\(\)") function **

##### Query

logscale
    
    
    fieldset()

##### Introduction

In this example, the [`fieldset()`](functions-fieldset.html "fieldset\(\)") function is used to request a list of all fields in a repository for HTTP access logs. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         fieldset()

Returns a list of all available fields in a repository for HTTP access logs. 

  3. Event Result set.




##### Summary and Results

The query is used to return a list of all fields within the current event set. The [`fieldset()`](functions-fieldset.html "fieldset\(\)") function is particularly useful when you are new to an event set, as it provides a quick way to get an overview of all available fields without having to inspect individual events manually. Also a valuable tool for further querying when combining it with other functions or filters to explore specific subsets of the data. 

Sample output from the incoming example data (HTTP access log): 

@timezone  
---  
@timestamp.nanos  
@timestamp  
@source  
@rawstring  
@ingesttimestamp  
@id  
@host  
#type  
#repo  
#humioBackfill  
  
The list of returned fields is context specific. The field list can be reduced as part of the query when combined with other functions, for example, by an aggregate function: 

logscale
    
    
    groupBy([#type,@host])
    | fieldset()

Sample output from the incoming example data when reduced: 

_count  
---  
@host  
#type
