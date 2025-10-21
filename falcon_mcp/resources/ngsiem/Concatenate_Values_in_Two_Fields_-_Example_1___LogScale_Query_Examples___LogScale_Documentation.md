# Concatenate Values in Two Fields - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-concat-aid-cid.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Values in Two Fields - Example 1

Concatenate values in two fields into a single value in a new array using the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    concat([aidValue, cidValue], as=checkMe2)

### Introduction

The [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function concatenates (joins) the values of a list of fields into a single value in a new field. The [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) method does not change the existing fields. The new field contains the merge between the concatenated values. 

In this example, the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function concatenates the AID (Agent ID) and CID (Customer ID) values into a single value in a new array. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         concat([aidValue, cidValue], as=checkMe2)

Concatenates the values of the fields aidValue and cidValue into a single value in a new field named checkMe2. 

The single value contains both the Agent ID and Customer ID information. It is recommended to have a consistent format and potentially include a separator between the AID and CID to ensure, that they can be easily parsed apart, if needed later. 

  3. Event Result set.




### Summary and Results

The query is used to concatenate the values of a list of fields into a single value in a new field. Combining CID and AID values is, for example, useful for unique identification, troubleshooting, data analysis etc. This query is also useful in case you want to combine for example first names and last names from two different fields into the full name in a new field, or if you have a list of users and a list of the URLs visited, that you want to combine to see which user navigated which URLs.
