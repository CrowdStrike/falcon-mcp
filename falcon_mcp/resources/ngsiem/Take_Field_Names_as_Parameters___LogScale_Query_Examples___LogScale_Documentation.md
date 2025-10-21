# Take Field Names as Parameters | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-getfield-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Take Field Names as Parameters

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | test(getField(?foo)==?bar)

### Introduction

Use the function to take a field name as a parameter. 

Given an event with the following fields: 
    
    
    |----------------------|
    | hello      | world   |
    |----------------------|

Test if a field exists on an event with a specific value where both the field and the value are given as parameters. This query: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | test(getField(?foo)==?bar)

Tests if the field given by the parameter `?foo (hello)` is equal to the value given by the parameter `?bar (world)`. 

  3. Event Result set.




### Summary and Results

hello  
---  
world
