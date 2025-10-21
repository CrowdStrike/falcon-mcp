# Annotate Events With Aggregation - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-stats-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Annotate Events With Aggregation - Example 1

Annotate events using [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function and aggregation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvParse()
    | stats([
    avg(x),
    table([x])
    ])

### Introduction

The [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function can be used to compute multiple aggregate functions over the input. 

In this example, the [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function is used with aggregation on the field x. 

Example incoming data might look like this: 

x=1  
---  
x=2  
x=9  
x=10  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | stats([
         avg(x),
         table([x])
         ])

Computes the aggregate functions [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) and [`table()`](https://library.humio.com/data-analysis/functions-table.html) over the field x, and returns the results in a field named _avg and a field named x. Note that the [`table()`](https://library.humio.com/data-analysis/functions-table.html) function returns more rows as output, whereas the [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) function only returns 1 row. 

  4. Event Result set.




### Summary and Results

The query is used to compute multiple aggregate functions over an input. 

Sample output from the incoming example data: 

_avg| x  
---|---  
5.5| 1  
5.5| 2  
5.5| 9  
5.5| 10
