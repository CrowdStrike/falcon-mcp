# Compute Aggregate Value for Each Array Element With Same Index | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-reducecolumn-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compute Aggregate Value for Each Array Element With Same Index

Compute an aggregate value for each array element with the same index using the [`array:reduceColumn()`](https://library.humio.com/data-analysis/functions-array-reducecolumn.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    maxTimes := array:reduceColumn(times, var=x, function={time := max(x)})

### Introduction

The [`array:reduceColumn()`](https://library.humio.com/data-analysis/functions-array-reducecolumn.html) function can be used to compute an aggregate value for each array element with the same index. 

In this example, the [`array:reduceColumn()`](https://library.humio.com/data-analysis/functions-array-reducecolumn.html) function is used to find the maximum time for each array element with same index in a flat array. 

Example incoming data might look like this: 

times[0]| times[1]| times[2]  
---|---|---  
1| 2| 3  
5| 1| 0  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         maxTimes := array:reduceColumn(times, var=x, function={time := max(x)})

Computes the maximum time for each array element with same index in the array and reduces it to one value. 

  3. Event Result set.




### Summary and Results

The query is used to find the maximum time for each array element with same index in a flat array. 

_reduceColumn[0]| _reduceColumn[1]| _reduceColumn[2]  
---|---|---  
5| 2| 3
