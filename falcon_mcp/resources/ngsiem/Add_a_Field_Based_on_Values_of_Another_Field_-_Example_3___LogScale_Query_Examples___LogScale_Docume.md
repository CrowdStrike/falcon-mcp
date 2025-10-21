# Add a Field Based on Values of Another Field - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-if-7.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Add a Field Based on Values of Another Field - Example 3

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | success := if(status < 500, then=if(status!=404, then=1, else=0), else=0)

### Introduction

Another example of nested [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions to add a field success and calculate its value based on field status. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | success := if(status < 500, then=if(status!=404, then=1, else=0), else=0)

Adds a success field at the following conditions: 

     * If the value of field status is less than `500`, set the value of success to `0`, but: 

     * If the value of field status is not equal to `404`, then set the value of success to `1` otherwise to `0`. 

  3. Event Result set.




### Summary and Results

Nested [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions for tagging a field according to different status values.
