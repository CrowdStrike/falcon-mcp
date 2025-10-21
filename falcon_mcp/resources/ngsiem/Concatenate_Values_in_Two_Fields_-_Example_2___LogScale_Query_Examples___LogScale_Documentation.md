# Concatenate Values in Two Fields - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-concat-f1-f2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Values in Two Fields - Example 2

Concatenate values in two fields into a single value in a new array using the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    concat([f1, f2], as="combined")

### Introduction

The [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function concatenates (joins) the values of a list of fields into a single value in a new field. The [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) method does not change the existing fields. The new field contains the merge between the concatenated values. 

In this example, the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function concatenates the values of two fields with different names (f1 and f2) into a single value in a new field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         concat([f1, f2], as="combined")

Concatenates the values of the arrays f1 and f2 into a single value in a new array named combined. 

  3. Event Result set.




### Summary and Results

The query is used to concatenate the values of a list of fields into a single value in a new field. This query is useful in case you want to combine for example first names and last names from two different fields into the full name in a new field, or if you have a list of users and a list of the URLs visited, that you want to combine to see which user navigated which URLs.
