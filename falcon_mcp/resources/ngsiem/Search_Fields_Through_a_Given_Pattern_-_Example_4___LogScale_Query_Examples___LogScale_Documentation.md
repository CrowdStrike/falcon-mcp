# Search Fields Through a Given Pattern - Example 4 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-wildcard-4.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Fields Through a Given Pattern - Example 4

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    wildcard(pattern=horse, ignoreCase=false)

### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
mammal| Horse  
mammal| wild horses  
animal| human  
mammal| HORSES  
animal| duck  
mammal| dog  
animal| dancing with horses  
  
Find events that contain `horse` in any field, case-sensitive: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         wildcard(pattern=horse, ignoreCase=false)

Searches the original, unmodified event for the string `horse`. 

  3. Event Result set.




### Summary and Results

The result accepts the events with `horse`, `wild horses` and `dancing with horses`. This query is equivalent to the freetext search `"horse"` .
