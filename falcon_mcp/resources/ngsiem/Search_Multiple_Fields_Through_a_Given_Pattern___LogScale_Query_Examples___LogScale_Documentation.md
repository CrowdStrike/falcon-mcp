# Search Multiple Fields Through a Given Pattern | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-wildcard-multi-field.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Multiple Fields Through a Given Pattern

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    wildcard(field=[plant,animal], pattern=horse, ignoreCase=false)

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
plant| daisy  
plant| horseflower  
  
Search multiple fields for a value allows you to find events where the field animal or plant contains the exact value `horse`, and makes it case-sensitive. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         wildcard(field=[plant,animal], pattern=horse, ignoreCase=false)

Searches elements in the fields animal and plant that match `horse`. 

  3. Event Result set.




### Summary and Results

The result is a list of events where either the field animal or plant has the exact value `horse`. 

The query used is equivalent to `animal="horse" plant="horse"`.
