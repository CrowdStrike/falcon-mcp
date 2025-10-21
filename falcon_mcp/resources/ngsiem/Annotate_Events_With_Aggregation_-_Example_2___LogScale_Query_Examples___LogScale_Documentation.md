# Annotate Events With Aggregation - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-stats-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Annotate Events With Aggregation - Example 2

Annotate events using [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function and aggregation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvParse()
    | stats([
    sum(x, as=sumX),
    avg(y, as=avgY),
    table([x, y])
    ])

### Introduction

The [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function can be used to compute multiple aggregate functions over the input. 

In this example, the [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function is used with aggregation on the field x where one of the subaggregators ([`avg(y)`](https://library.humio.com/data-analysis/functions-avg.html)) outputs zero rows. 

The example shows what happens, when a subaggregator `avg(y)` does not produce an output. 

Example incoming data might look like this: 

logscale
    
    
    "x=1 y=N/A"
    "x=2 y=N/A"

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | stats([
         sum(x, as=sumX),
         avg(y, as=avgY),
         table([x, y])
         ])

Computes the aggregate functions [`sum()`](https://library.humio.com/data-analysis/functions-sum.html), [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) and [`table()`](https://library.humio.com/data-analysis/functions-table.html) over the fields x and y, and returns the results in a field named sumX, a field named x, and a field named y. 

  4. Event Result set.




### Summary and Results

The query is used to compute multiple aggregate functions over an input. 

Sample output from the incoming example data: 
    
    
    "sumX","x","y"
    "3","1","N/A"
    "3","2","N/A"
