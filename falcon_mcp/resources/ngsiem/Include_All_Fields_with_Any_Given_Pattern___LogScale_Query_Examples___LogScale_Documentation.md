# Include All Fields with Any Given Pattern | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-wildcard-8.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Include All Fields with Any Given Pattern

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    wildcard(field=animal, pattern=*, includeEverythingOnAsterisk=true)

### Introduction

Given the following three events: 

animal = horse  
---  
animal = seahorse  
machine = car  
  
Match all events in the result set — even those missing the animal field specified in [_`field`_](https://library.humio.com/data-analysis/functions-wildcard.html#query-functions-wildcard-field). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         wildcard(field=animal, pattern=*, includeEverythingOnAsterisk=true)

Set [_`pattern`_](https://library.humio.com/data-analysis/functions-wildcard.html#query-functions-wildcard-pattern) to `*` and include the [_`includeEverythingOnAsterisk`_](https://library.humio.com/data-analysis/functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk) parameter in the query. 

  3. Event Result set.




### Summary and Results

The result is a list of the following accepted events: 

field| value  
---|---  
animal| horse  
animal| seahorse  
machine| car  
  
Without [_`includeEverythingOnAsterisk`_](https://library.humio.com/data-analysis/functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk) ([_`includeEverythingOnAsterisk=false`_](https://library.humio.com/data-analysis/functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk)), only events with `animal` as the argument would match. For example: 

field| value  
---|---  
animal| horse  
animal| seahorse
