# Check for Values in Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-contains-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check for Values in Array

Use array query filter [`array:contains()`](https://library.humio.com/data-analysis/functions-array-contains.html) to check for a value in a flat array 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:contains("incidents[]", value="Cozy Bear")

### Introduction

Array query filters are data structure elements that make it possible to define a list of values in a single field. The different array query functions can be used to extract, filter and search data and then index it into an array. 

In this example, the [`array:contains()`](https://library.humio.com/data-analysis/functions-array-contains.html) function is used to check if a given value exists in a given array. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:contains("incidents[]", value="Cozy Bear")

Checks if the value of `Cozy Bear` exists within the incidents array field. If the array contains the value, the whole event is included in the search result. 

  3. Event Result set.




### Summary and Results

The query is used as a filter to check if a given value exists in a given array within the event set. If the given value does not match any of the values of the array, then the event is excluded from the search result. Arrays are used when ingesting security event logs where fields may have more than one value. If the array contains other values along with the specified value, these are also included in the search results.
