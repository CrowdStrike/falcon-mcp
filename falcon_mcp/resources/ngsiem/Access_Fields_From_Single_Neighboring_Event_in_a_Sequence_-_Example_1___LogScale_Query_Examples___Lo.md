# Access Fields From Single Neighboring Event in a Sequence - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-neighbor-preceeding.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Access Fields From Single Neighboring Event in a Sequence - Example 1

Access fields from a single neighboring (preceeding) event in a sequence using the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | neighbor(key, prefix=prev)

### Introduction

The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to look at data from nearby events in a defined sequence. 

In this example, the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function is used to look at the preceeding event; the one just before the current event as no distance is specified. 

Note that the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

key  
---  
a  
a  
b  
c  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | neighbor(key, prefix=prev)

For each event, looks at the event immediately before it, and returns the value of the field key within the current event as a field named prev.key. 

It is also possible to look at an event further away, if defining a distance: `neighbor(key, prefix=prev, distance=2)`

  4. Event Result set.




### Summary and Results

In this example, the value of a field from a preceding event is added to each event. 

Sample output from the incoming example data: 

key| prev.key  
---|---  
a| <no value>  
a| a  
b| a  
c| b  
  
The query is useful for comparing events or detecting patterns in sequential data.
