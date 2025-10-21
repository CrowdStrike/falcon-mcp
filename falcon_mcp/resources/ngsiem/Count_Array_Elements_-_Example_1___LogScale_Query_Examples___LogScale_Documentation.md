# Count Array Elements - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-length-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Array Elements - Example 1

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

### Introduction

Given an event that has multiple queryParserMetrics.function[] array fields (a list of the functions used in a query): 

queryParserMetrics.function[0]="head"  
---  
queryParserMetrics.function[1]="bucket"  
queryParserMetrics.functions[2]="groupBy"  
  
We want to get the number of functions listed in the `queryParserMetrics.function[]` arrays for that event. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:length("queryParserMetrics.function[]", as="_numberOfFunctions")

Counts the elements (the functions in the array) in the `queryParserMetrics.function[]` array field. 

  3. Event Result set.




### Summary and Results

The returned value is the number of functions found in the array, and it will be output into the _numberOfFunctions field, which is set by the argument [_`as`_](https://library.humio.com/data-analysis/functions-array-length.html#query-functions-array-length-as). 

_numberOfFunctions| 3  
---|---
