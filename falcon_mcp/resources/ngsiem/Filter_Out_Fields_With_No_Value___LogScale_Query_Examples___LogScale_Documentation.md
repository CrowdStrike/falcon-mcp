# Filter Out Fields With No Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-sort-excludenovalue.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Out Fields With No Value

Filter out fields with no values from search results 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    method=GET
    groupBy(field=[method, statuscode], function=count(as=method_total))
    sort([method, statuscode], order=asc)
    FieldName!=""

### Introduction

It is possible to filter out on fields with no values in a given returned search result. In this example, all statuscode fields containing no value is filtered out from the final search result. 

Example incoming data might look like this: 

method| statuscode| method_total  
---|---|---  
GET| <no value>| 10  
GET| 200| 32492  
GET| 301| 1  
GET| 304| 113  
GET| 403| 9  
GET| 404| 132  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         method=GET

Filters for all events with methods of the type `GET`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(field=[method, statuscode], function=count(as=method_total))

Groups the returned results into a method field and a statuscode field and makes a count of the events in a new field named method_total. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sort([method, statuscode], order=asc)

Sorts the returned results in ascending order. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         FieldName!=""

Excludes all events where one of the fields do not contain a value. 

  6. Event Result set.




### Summary and Results

The query is used to filter out fields not containing any values from the returned search result. 

Sample output from the incoming example data: 

method| statuscode| method_total  
---|---|---  
GET| 200| 32492  
GET| 301| 1  
GET| 304| 113  
GET| 403| 9  
GET| 404| 132
