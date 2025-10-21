# Search Fields Through a Given Pattern - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-wildcard-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Fields Through a Given Pattern - Example 3

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    wildcard(field=animal, pattern=*h*rse*, ignoreCase=true)

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
  
Finds events where field animal matches the given pattern, and it's case-insensitive: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         wildcard(field=animal, pattern=*h*rse*, ignoreCase=true)

Searches elements in the field animal that match `*h*rse*`. 

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
hooorse  
  
The query used is equivalent to: `animal=/h.*rse/i` . 

Note that it is unanchored.
