# Filter on a Single Field for One Specific Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-singlevalue.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter on a Single Field for One Specific Value

Filter the events using a single field matching a specific value 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    status = 404

### Introduction

In this example we want a list of events in which the user received the HTTP code `404`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         status = 404

Filters for all events with the value `404` in the status field. 

  3. Event Result set.




### Summary and Results

The query is used to search a single field for one specific value. In this example, it selects logs with a specific HTTP status.
