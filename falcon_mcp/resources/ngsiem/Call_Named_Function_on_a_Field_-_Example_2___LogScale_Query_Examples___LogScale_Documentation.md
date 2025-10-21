# Call Named Function on a Field - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-callfunction-timechart-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Call Named Function on a Field - Example 2

Calls the named function ([`count()`](https://library.humio.com/data-analysis/functions-count.html)) on a field over a set of events 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(function=[callFunction(?{function=count}, field=value)])

### Introduction

The [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html) function calls a specific function. The parameters of the called funcion are passed as parameters in [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html). 

In this example, the [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html) function is used to call the named function ([`count()`](https://library.humio.com/data-analysis/functions-count.html)) on a field over a set of events using the query parameter `?function`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(function=[callFunction(?{function=count}, field=value)])

Counts the events in the value field, and displays the results in a timechart. 

Notice how the query parameter `?function` is used to select the aggregation function for a [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html). 

  3. Event Result set.




### Summary and Results

The query is used to count events and chart them over time. Because we are using [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html), it could be a different function based on the dashboard parameter. 

Using a query parameter (for example, `?function`) to select the aggregation function for a [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) is useful for dashboard widgets. 

Using [`callFunction()`](https://library.humio.com/data-analysis/functions-callfunction.html) allow for using a function based on the data or dashboard parameter instead of writing the query directly.
