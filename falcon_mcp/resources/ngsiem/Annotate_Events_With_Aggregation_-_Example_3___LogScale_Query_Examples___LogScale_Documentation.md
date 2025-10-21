# Annotate Events With Aggregation - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-stats-3-cartesian.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Annotate Events With Aggregation - Example 3

Annotate events using [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function and aggregation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvParse()
    | stats([
    table([x,y]),
    table([z])
    ])

### Introduction

The [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function can be used to compute multiple aggregate functions over the input. 

In this example, the [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function is used with aggregation on the fields x, y, and z, where all of the subaggregators output rows. 

The example shows a Cartesian product where the output is all combinations of all results of the subaggregators 

Example incoming data might look like this: 

logscale
    
    
    "x=1 y=10 z=100"
    "x=2 y=20 z=200"

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | stats([
         table([x,y]),
         table([z])
         ])

Computes the aggregate function [`table()`](https://library.humio.com/data-analysis/functions-table.html) over the fields x, y, and z, and returns the results - a combination of all outputs, also called the Cartesian product - in a field named x, a field named y, and a field named z. Note that since both subaggregators output multiple rows, the returned result is the Cartesian product, containing all combinations of the results from the subaggregators. 

  4. Event Result set.




### Summary and Results

The query is used to compute multiple aggregate functions over an input. 

Sample output from the incoming example data: 

x| y| z  
---|---|---  
1| 10| 100  
1| 10| 200  
2| 20| 100  
2| 20| 200
