# Add a Field Based on Values of Another Field - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-if-6.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Add a Field Based on Values of Another Field - Example 2

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | success := if(status >= 500, then=0, else=if(status == 404, then=0, else=1))

### Introduction

Another example of nested [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions: this is used to add a field success whose value is calculated based on field status. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | success := if(status >= 500, then=0, else=if(status == 404, then=0, else=1))

Adds a success field at the following conditions: 

     * Sets the value of field success to `0` if status is greater or equal to `500` or if it's equal to `400`, otherwise: 

     * Sets the value of field success to `1`. 

  3. Event Result set.




### Summary and Results

Nested [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions for tagging a field according to different status values.
