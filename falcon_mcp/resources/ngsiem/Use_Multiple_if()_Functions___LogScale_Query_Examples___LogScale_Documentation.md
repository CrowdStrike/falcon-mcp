# Use Multiple if() Functions | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-if-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Use Multiple if() Functions

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    score := if(x != "N/A", then=x, else=0) +  if(y != "N/A", then=y, else=0)

### Introduction

Multiple [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions can be used in a computation (eval/assign). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         score := if(x != "N/A", then=x, else=0) +  if(y != "N/A", then=y, else=0)

This computation checks if fields x or y is not a number, then `0` will be used instead. 

  3. Event Result set.




### Summary and Results

Setting the value based on an incoming value enables determination of a score triggered by a value.
