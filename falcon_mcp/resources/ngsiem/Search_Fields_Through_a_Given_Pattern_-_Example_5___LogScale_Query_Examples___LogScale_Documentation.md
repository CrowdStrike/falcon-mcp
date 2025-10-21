# Search Fields Through a Given Pattern - Example 5 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-wildcard-5.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Fields Through a Given Pattern - Example 5

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    wildcard(pattern=horse, ignoreCase=true)

### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
animal| Horse  
animal| duck  
animal| HORSES  
animal| crazy hOrSe  
animal| hooorse  
animal| dancing with horses  
  
Finds events that contain `horse`, case-insensitive: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         wildcard(pattern=horse, ignoreCase=true)

Searches the original, unmodified event for the string `horse`, case-insensitive. 

  3. Event Result set.




### Summary and Results

The result is a list of the following accepted events: 

animal  
---  
horse  
Horse  
HORSES  
crazy hOrSe  
dancing with horses  
  
This query is equivalent to the freetext regex `/horse/i` .
