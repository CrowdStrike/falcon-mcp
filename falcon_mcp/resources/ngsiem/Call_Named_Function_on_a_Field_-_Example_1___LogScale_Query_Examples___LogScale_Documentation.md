# Call Named Function on a Field - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-callfunction-avg.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Call Named Function on a Field - Example 1

Calls the named function ([`avg()`](https://library.humio.com/data-analysis/functions-avg.html)) on a field over a set of events 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    avg_sent:=callFunction("avg", field=bytes_sent)

### Introduction

The [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html) function calls a specific function. The parameters of the called function are passed as parameters in [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html). 

In this example, the [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html) function is used to find the average bytes sent in HTTP responses. It calls the named function ([`avg()`](https://library.humio.com/data-analysis/functions-avg.html)) on a field over a set of events. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         avg_sent:=callFunction("avg", field=bytes_sent)

Finds the average bytes sent in HTTP response, and returns the results in a new field named avg_sent. Notice that the [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) function is used indirectly in this example. 

  3. Event Result set.




### Summary and Results

The query is used to find the average bytes sent in HTTP responses. Using a query parameter (for example, `?function`) to select the aggregation function for a [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) is useful for dashboard widgets. 

Using [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html) allow for using a function based on the data or dashboard parameter instead of writing the query directly.
