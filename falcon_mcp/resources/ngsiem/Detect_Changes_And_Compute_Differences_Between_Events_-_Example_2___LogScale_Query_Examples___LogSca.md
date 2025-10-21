# Detect Changes And Compute Differences Between Events - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-neighbor-changes-example-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Detect Changes And Compute Differences Between Events - Example 2

Detect changes and compute differences between events using the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function combined with [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    head()
    | neighbor(start, prefix=prev)
    | duration := start - prev.start
    | accumulate(sum(duration, as=accumulated_duration))

### Introduction

The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to look at data from nearby events in a defined sequence. The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to compare an event with events that came before or after it, to identify patterns in a data sequence and to analyze how data changes from one event to the next. 

In this example, the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function is used with [`accumulate()`](https://library.humio.com/data-analysis/functions-accumulate.html) to calculate a running total of durations. 

Note that the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

start  
---  
1100  
1233  
3002  
4324  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | neighbor(start, prefix=prev)

Retrieves the value in the start field from preceeding event, and assigns this value to the current event's data in a new field named prev.start. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | duration := start - prev.start

Calculates the time difference between current and previous start values, and returns the results - the calculated difference - in a field named duration. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | accumulate(sum(duration, as=accumulated_duration))

Calculates a running total sum of the values in the field duration and returns the results in a field named accumulated_duration. Each event will show its individual duration and the total accumulated duration up to that point. 

  6. Event Result set.




### Summary and Results

The query is used to calculate the time difference between consecutive events. The format of this query is a useful pattern when analyzing temporal data, to provide insights into process efficiency, system performance over time etc. In this example, the acculated_duration provides a value that can be used to compare against the duration field within each event. 

Sample output from the incoming example data: 

start| accumulated_duration| duration| prev.start  
---|---|---|---  
1100| 0| <no value>| <no value>  
1233| 133| 133| 1100  
3002| 1902| 1769| 1233  
4324| 3224| 1322| 3002  
  
For example, in the results, the third event shows a large increase in duration against the accumulated_duration and the start time of the previous event (in prev.start). If analyzing execution times of a process, this could indicate a fault or delay compared to previous executions.
