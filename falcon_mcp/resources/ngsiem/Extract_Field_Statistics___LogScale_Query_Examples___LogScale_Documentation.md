# Extract Field Statistics | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-fieldstats-totalcount.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Field Statistics

Extract field statistics from a repository using the [`fieldstats()`](https://library.humio.com/data-analysis/functions-fieldstats.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    fieldstats()

### Introduction

The [`fieldstats()`](https://library.humio.com/data-analysis/functions-fieldstats.html) function can be used to provide the distinct count and total count for a field in a event set. The function returns an event set that contains statistics for the fields in the current event set. 

In this example, the [`fieldstats()`](https://library.humio.com/data-analysis/functions-fieldstats.html) function is used to get the statistics for the fields #type, field, _count and distinct within the HUMIO repository. The example will only show the first 20 rows (but the [_`limit`_](https://library.humio.com/data-analysis/functions-fieldstats.html#query-functions-fieldstats-limit) parameter has a default value of `200` rows. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         fieldstats()

Extracts statistics about fields within the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) respository. 

  3. Event Result set.




### Summary and Results

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
