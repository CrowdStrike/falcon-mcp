# Access Fields From Single Neighboring Event in a Sequence - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-neighbor-succeeding.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Access Fields From Single Neighboring Event in a Sequence - Example 2

Access fields from a single neighboring (succeeding) event in a sequence using the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | neighbor(key, prefix=succ, direction=succeeding)

### Introduction

The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to look at data from nearby events in a defined sequence. The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to compare an event with events that came before or after it, to identify patterns in a data sequence and to analyze how data changes from one event to the next. 

In this example, the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function is used to look at the succeeding event; the one just after the current event as no distance is specified. 

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
         
         | neighbor(key, prefix=succ, direction=succeeding)

For each event, looks at the event immediately after it, and returns the results in a field named succ.key. 

  4. Event Result set.




### Summary and Results

The query is used to access fields from a single neighboring event in a sequence, retrieving fields from either a preceding or succeeding event at a specified distance (number of events) from the current event. 

Sample output from the incoming example data: 

key| succ.key  
---|---  
a| a  
a| b  
b| c  
c| <no value>  
  
The query is useful for comparing event values or detecting patterns in sequential data.
