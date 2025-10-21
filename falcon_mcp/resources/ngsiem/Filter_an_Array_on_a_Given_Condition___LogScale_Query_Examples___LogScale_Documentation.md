# Filter an Array on a Given Condition | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-filter-condition.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter an Array on a Given Condition

Filter the elements of a flat array on a given condition using the array filter function [`array:filter()`](https://library.humio.com/data-analysis/functions-array-filter.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:filter(array="mailto[]", var="addr", function={addr=ba*@example.com}, asArray="out[]")

### Introduction

It is possible to filter an array on a given condition using the array filter function [`array:filter()`](https://library.humio.com/data-analysis/functions-array-filter.html). The [`array:filter()`](https://library.humio.com/data-analysis/functions-array-filter.html) creates a new array with elements matching the specified conditions and does not change the original array. The new array will retain the original order. 

Example incoming data might look like this: 

logscale
    
    
    mailto[0]=foo@example.com
    mailto[1]=bar@example.com
    mailto[2]=baz@example.com

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:filter(array="mailto[]", var="addr", function={addr=ba*@example.com}, asArray="out[]")

Filters the mailto[] array to include only elements that contain the value `ba*@example.com`, this is achieved by testing the value of each element of the array, set by the [_`var`_](https://library.humio.com/data-analysis/functions-array-filter.html#query-functions-array-filter-var) parameter as `addr`, returning a new array that only contains elements that meet the specified condition. The expression in the [_`function`_](https://library.humio.com/data-analysis/functions-array-filter.html#query-functions-array-filter-function) argument should contain the field declared in the _`addr`_ parameter. 

  3. Event Result set.




### Summary and Results

The query is used to filter values from the input array using the function provided in the array and return a new array with the results meeting the specified condition. 

Sample output from the incoming example data: 

logscale
    
    
    out[0]=bar@example.com
    out[1]=baz@example.com
