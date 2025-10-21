# Access Fields From Single Neighboring Event in a Sequence - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-neighbor-furtheraway.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Access Fields From Single Neighboring Event in a Sequence - Example 3

Access fields from a single neighboring (further away) event in a sequence using the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | neighbor(key, prefix=prev, distance=2)

### Introduction

The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to look at data from nearby events in a defined sequence. The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to compare an event with events that came before or after it, to identify patterns in a data sequence and to analyze how data changes from one event to the next. 

In this example, the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function is used to look at a preceeding event with the specified distance of `2` away from the current event. 

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
         
         | neighbor(key, prefix=prev, distance=2)

For each event, looks two events back in the sequence. It retrieves the key value from that event two positions back, and adds this value to the current event's data, labeled with prev.key. 

  4. Event Result set.




### Summary and Results

The query is used to access fields from each event at a specified distance (number of events) away in a sequence of events, retrieving fields from either a preceding or succeeding event at a specified distance from the current event. 

Sample output from the incoming example data: 

key| prev.key  
---|---  
a| <no value>  
a| <no value>  
b| a  
c| a  
  
The query is useful for comparing events with others that are not immediately adjacent in your data sequence.
