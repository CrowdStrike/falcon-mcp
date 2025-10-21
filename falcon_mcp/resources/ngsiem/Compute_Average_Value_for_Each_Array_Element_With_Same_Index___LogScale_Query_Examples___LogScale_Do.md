# Compute Average Value for Each Array Element With Same Index | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-reducecolumn.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compute Average Value for Each Array Element With Same Index

Compute an average value for each array element with the same index across multiple events using the [`array:reduceColumn()`](https://library.humio.com/data-analysis/functions-array-reducecolumn.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    maxTimes := array:reduceColumn("ages[]", var=x, function=avg(x))

### Introduction

The [`array:reduceColumn()`](https://library.humio.com/data-analysis/functions-array-reducecolumn.html) function can be used to compute an average value for each array element with the same index. 

In this example, the [`array:reduceColumn()`](https://library.humio.com/data-analysis/functions-array-reducecolumn.html) function is used to find the maximum time for each array element with same index in a flat array. 

Example incoming data might look like this: 

ages[0]| ages[1]| ages[2]  
---|---|---  
16| 32| 64  
15| 30| 45  
1| 2| 4  
89| 57| 67  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         maxTimes := array:reduceColumn("ages[]", var=x, function=avg(x))

Computes the average for each array element with same index in the array and reduces it to one value, placing the result for each index into a new field _reduceColumn. 

  3. Event Result set.




### Summary and Results

The query is used to find the maximum time for each array element with same index in a flat array. 

_reduceColumn[0]| _reduceColumn[1]| _reduceColumn[2]| _reduceColumn[3]  
---|---|---|---  
40.3| 40.3| 63.3|
