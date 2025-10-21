# Detect Changes And Compute Differences Between Events - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-neighbor-changes-example-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Detect Changes And Compute Differences Between Events - Example 1

Detect changes and compute differences between events using the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    head()
    | neighbor(value, prefix=prev)
    | change := value - prev.value
    | change > 5

### Introduction

The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to look at data from nearby events in a defined sequence. The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to compare an event with events that came before or after it, to identify patterns in an event sequence and to analyze how data changes from one event to the next. 

In this example, the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function is used to detect changes in values and alert on large increase. 

Note that the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

value  
---  
3  
5.5  
4  
10  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | neighbor(value, prefix=prev)

Retrieves the value from preceeding event, and assigns this value to the current event's data in a new field named prev.value. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | change := value - prev.value

Calculates the difference between current and previous values, and returns the results - the calculated difference - in a field named change. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | change > 5

Filters for values in the field change to show only events where the change is greater than `5`. 

  6. Event Result set.




### Summary and Results

The query is used to detect changes in values and alert on a quantified increase. The query will identify events where the value has increased by more than 5 compared to the previous event. 

Sample output from the incoming example data: 

value| change| prev.value  
---|---|---  
10| 6| 4  
  
The query is useful for real-time monitoring and alerting systems where you need to quickly identify significant changes in sequential data. It allows for immediate detection of anomalies or important shifts in your data, enabling prompt responses to potential issues or opportunities.
