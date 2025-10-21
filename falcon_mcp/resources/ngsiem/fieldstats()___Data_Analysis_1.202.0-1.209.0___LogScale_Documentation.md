# fieldstats() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-fieldstats.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`fieldstats()`](functions-fieldstats.html "fieldstats\(\)")

Displays statistics about the fields within the current event stream. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`limit`_](functions-fieldstats.html#query-functions-fieldstats-limit)|  integer| optional[a] | `200`|  Limits the number of fields to generate statistics for.   
|  | **Minimum**| `1`|   
|  | **Maximum**| `10,000`|   
[a] Optional parameters use their default value unless explicitly set.  
  
### [`fieldstats()`](functions-fieldstats.html "fieldstats\(\)") Function Operation

The function returns an event set that contains statistics for the fields in the current event set; the returned fields include: 

  * [#type](searching-data-event-fields.html#searching-data-event-fields-tag-type)

The name of the parser used when the data was ingested. When viewing events that may have been extracted by multiple parsers the type will be shown for each elevant field in the event set. 

  * field

The name of field. 

  * _count

The number of values for the named field within the event set. 

  * distinct

The number of distinct values for the named field in the event set. 




### [`fieldstats()`](functions-fieldstats.html "fieldstats\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Field Statistics

**Extract field statistics from a repository using the[`fieldstats()`](functions-fieldstats.html "fieldstats\(\)") function **

##### Query

logscale
    
    
    fieldstats()

##### Introduction

In this example, the [`fieldstats()`](functions-fieldstats.html "fieldstats\(\)") function is used to get the statistics for the fields #type, field, _count and distinct within the HUMIO repository. The example will only show the first 20 rows (but the [_`limit`_](functions-fieldstats.html#query-functions-fieldstats-limit) parameter has a default value of `200` rows. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         fieldstats()

Extracts statistics about fields within the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) respository. 

  3. Event Result set.




##### Summary and Results

The query is used to extract statistics about the fields within a current event stream. The process of extracting insights from data streams in real time or near-real time can be used to identify and act on critical business moments, collect data from various sources, and to understand the meaning of this data and its content. Statistics are useful for analyzation. 

Sample output from the incoming example data (showing the first 20 rows only): 

#type| field| _count| distinct  
---|---|---|---  
humio| decodedContentLength| 60501| 107  
humio| originalName| 154824| 19  
humio| tx_fifo| 16296| 1  
humio| humioClass| 1641588| 320  
humio| p75| 268658| 42439  
humio| bucketId| 234418| 2  
humio| dataspaceId| 10077935| 56  
humio| userAgent| 61675| 7  
humio| datasource| 9037297| 143  
humio| request-rate| 43678| 24248  
humio| topic_leader_size| 18611| 16112  
humio| readOnly| 158036| 1  
humio| request-latency-avg| 39542| 7169  
humio| @rawstring| 17517915| 17696022  
humio| percentDone| 85431| 39209  
humio| uri| 61675| 325  
humio| tx_carrier| 16296| 1  
humio| p98| 268658| 45969  
humio| totalCount| 42731| 9  
humio| s3AccessConfig| 158036| 1
