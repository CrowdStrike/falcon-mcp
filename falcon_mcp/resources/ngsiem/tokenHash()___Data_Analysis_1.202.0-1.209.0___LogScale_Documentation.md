# tokenHash() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-tokenhash.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jul 23, 2025

## [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)")

Calculates a "structure hash" which is equal for similarly structured input. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-tokenhash.html#query-functions-tokenhash-as)|  string| optional[a] | `_tokenHash`|  The name of output field.   
[_`field`_](functions-tokenhash.html#query-functions-tokenhash-field)[b]| string| required |  |  The name of the field to hash.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-tokenhash.html#query-functions-tokenhash-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-tokenhash.html#query-functions-tokenhash-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     tokenHash("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     tokenHash(field="value")
> 
> These examples show basic structure only.

### [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") Syntax Examples

The [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") tokenizes the incoming string (separated by spaces), and then creates a hash for each tokenised elements and adds them together. The hash generated in this form will therefore consistent, providing each token in the input is identical, irrespective of the order. For example, the following two log lines contain the same information even though the order of each word is different: 

valueString  
---  
abc def ghi  
def ghi abc  
  
Executing [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") on each will generate the same hash value: 

logscale
    
    
    tokenHash(field=valueString)

This generates the same hash value for both rows, even though the order of each word is different: 

_tokenHash  
---  
84edeb8f  
84edeb8f  
  
This can be useful to compare, filter or deduplicate log lines during parsing or querying even though the order of the individual values within a set of key/value pairs might be different. 

### [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") Examples

Click + next to an example below to get the full details.

#### Group Similar Log Lines Using TokenHash

**Find patterns in log messages by grouping similar structures using the[`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") function **

##### Query

logscale
    
    
    h := tokenHash(@rawstring)
    groupBy(h, limit=max, function=[ count(), collect(@rawstring, limit=3) ])

##### Introduction

In this example, the [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") function is used to group log messages that share the same structure but contain different values. This helps identify common log patterns in your data. 

Note that the purpose of [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") is for grouping related log lines, not for cryptographic use. 

Example incoming data might look like this: 

@timestamp| @rawstring  
---|---  
2023-06-06T10:00:00Z| User john.doe logged in from 192.168.1.100  
2023-06-06T10:01:00Z| User jane.smith logged in from 192.168.1.101  
2023-06-06T10:02:00Z| User admin logged in from 192.168.1.102  
2023-06-06T10:03:00Z| Failed login attempt from 10.0.0.1  
2023-06-06T10:04:00Z| Failed login attempt from 10.0.0.2  
2023-06-06T10:05:00Z| Database connection error: timeout after 30 seconds  
2023-06-06T10:06:00Z| Database connection error: timeout after 45 seconds  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         h := tokenHash(@rawstring)

Creates a hash value based on the structure of the log message in the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field and returns the token hash in a new field named h. The [`tokenHash()`](functions-tokenhash.html "tokenHash\(\)") function identifies words, numbers, and special characters while ignoring their specific values. 

  3. logscale
         
         groupBy(h, limit=max, function=[ count(), collect(@rawstring, limit=3) ])

Groups the events by the token hash in the field h. For each group, it: 

     * Counts the number of events using [`count()`](functions-count.html "count\(\)"). 

     * Collects up to three example log messages using [`collect()`](functions-collect.html "collect\(\)") on the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field. 

The [_`limit`_](functions-groupby.html#query-functions-groupby-limit)=max parameter ensures all groups are returned. 

  4. Event Result set.




##### Summary and Results

The query is used to identify common log message patterns by grouping similar log lines together, regardless of their specific values. 

This query is useful, for example, to discover the most common types of log messages in your data, identify unusual or rare log patterns that might indicate problems and create log message templates for parsing or monitoring. 

Sample output from the incoming example data: 

h| _count| @rawstring  
---|---|---  
1111b796| 3| User admin logged in from 192.168.1.102 User jane.smith logged in from 192.168.1.101 User john.doe logged in from 192.168.1.100  
356fb767| 2| Failed login attempt from 10.0.0.2 Failed login attempt from 10.0.0.1  
90fadc1e| 2| Database connection error: timeout after 45 seconds Database connection error: timeout after 30 seconds  
  
Note that logs with the same structure but different values are grouped together, making it easy to identify common patterns in your log data.
