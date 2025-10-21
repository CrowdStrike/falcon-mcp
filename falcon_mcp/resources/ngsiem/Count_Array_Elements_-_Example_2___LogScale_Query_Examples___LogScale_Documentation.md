# Count Array Elements - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-length-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Array Elements - Example 2

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    queryParserMetrics.function[0] = "head"
    | array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

### Introduction

Given an event that has the queryParserMetrics.function[] array fields (a list of the functions used in a query): 

queryParserMetrics.function[0]="head"  
---  
queryParserMetrics.function[1]="bucket"  
queryParserMetrics.functions[2]="groupBy"  
  
Filters only events that has `head` as the value of queryParserMetrics.function[] array field, and then gets the number of functions listed in the `queryParserMetrics.function[]` array for that event. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         queryParserMetrics.function[0] = "head"

Filters events that has `head` as the value of queryParserMetrics.function[0] array field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

Counts the elements (the functions used) in all the `queryParserMetrics.function[]` arrays for that event. 

  4. Event Result set.




### Summary and Results

You will get an array of all the functions used in just one event where `head` is the first function used. The result will be output into the _numberOfFunctions field set by the argument [_`as`_](https://library.humio.com/data-analysis/functions-array-length.html#query-functions-array-length-as). 

_numberOfFunctions| 1  
---|---
