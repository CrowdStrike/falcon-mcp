# Request List of Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-fieldset-list.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Request List of Fields

Request a list of all fields in a repository using the [`fieldset()`](https://library.humio.com/data-analysis/functions-fieldset.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    fieldset()

### Introduction

The [`fieldset()`](https://library.humio.com/data-analysis/functions-fieldset.html) function can be used to return a list of all available fields in a repository. It returns everything within the current event set. The list of returned fields is context specific. 

In this example, the [`fieldset()`](https://library.humio.com/data-analysis/functions-fieldset.html) function is used to request a list of all fields in a repository for HTTP access logs. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         fieldset()

Returns a list of all available fields in a repository for HTTP access logs. 

  3. Event Result set.




### Summary and Results

The query is used to return a list of all fields within the current event set. The [`fieldset()`](https://library.humio.com/data-analysis/functions-fieldset.html) function is particularly useful when you are new to an event set, as it provides a quick way to get an overview of all available fields without having to inspect individual events manually. Also a valuable tool for further querying when combining it with other functions or filters to explore specific subsets of the data. 

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
