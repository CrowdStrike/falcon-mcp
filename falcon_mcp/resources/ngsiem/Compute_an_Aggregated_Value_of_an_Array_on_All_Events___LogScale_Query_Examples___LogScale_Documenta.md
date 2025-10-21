# Compute an Aggregated Value of an Array on All Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-reduceall-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compute an Aggregated Value of an Array on All Events

Compute an aggregated value of a flat array on all events using the [`array:reduceAll()`](https://library.humio.com/data-analysis/functions-array-reduceall.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:reduceAll("values[]", var=x, function=max(x))

### Introduction

The [`array:reduceAll()`](https://library.humio.com/data-analysis/functions-array-reduceall.html) function computes a value across all events and array elements of the specified array. The `reduce()` method returns a single value: the function's accumulated result. 

In this example, the aggregate function [`max()`](https://library.humio.com/data-analysis/functions-max.html) is used to output a single event with a single field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:reduceAll("values[]", var=x, function=max(x))

Computes the maximum value over all the values within the array values[] by using the [`max()`](https://library.humio.com/data-analysis/functions-max.html) on each element, and then across each event in the event set. 

  3. Event Result set.




### Summary and Results

The query is used to compute a value from all events and array elements of a specified array. The `reduce()` method is recommended, when you need to have a single value returned from iterating over your array. Only aggregate functions that return a single event with a single field (such as [`avg()`](https://library.humio.com/data-analysis/functions-avg.html), [`count()`](https://library.humio.com/data-analysis/functions-count.html), [`sum()`](https://library.humio.com/data-analysis/functions-sum.html), [`max()`](https://library.humio.com/data-analysis/functions-max.html) etc.) are allowed as the [_`function`_](https://library.humio.com/data-analysis/functions-array-reduceall.html#query-functions-array-reduceall-function) argument.
