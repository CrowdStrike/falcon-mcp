# Aggregate Array Content | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-contains.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Aggregate Array Content

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    array:contains("incidents[]", value="Cozy Bear")
    | groupBy(host)

### Introduction

Given events containing an `incidents` array: 

Event 1 
    
    
    |--------------|-------------|
    | host         | v1          |
    | incidents[0] | Evil Bear   |
    | incidents[1] | Cozy Bear   |
    |--------------|-------------|

Event 2 
    
    
    |--------------|-------------|
    | host         | v15         |
    | incidents[0] | Fancy Fly   |
    | incidents[1] | Tiny Cat    |
    | incidents[2] | Cozy Bears  |
    |--------------|-------------|

Finds all the events where the field incidents contains the exact value `Cozy Bear` and group them by which hosts were affected, giving output event: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:contains("incidents[]", value="Cozy Bear")

Extracts elements from the array incidents from the field host that match the text `Cozy Bear`. The items will be output into the host field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(host)

Groups the result events extracted from the array by the host. 

  4. Event Result set.




### Summary and Results

The result is an aggregated count of the array elements matching `Cozy Bear`. 

field| value  
---|---  
host| v1  
_count| 1
