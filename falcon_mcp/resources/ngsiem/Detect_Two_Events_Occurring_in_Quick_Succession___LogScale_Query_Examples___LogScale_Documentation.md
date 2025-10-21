# Detect Two Events Occurring in Quick Succession | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-slidingtimewindow-groupby-detect-quick-succession.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Detect Two Events Occurring in Quick Succession

Detect event B occurring quickly after event A using the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    head()
    | slidingTimeWindow(
        [{event = "A" | count(event, as=countAs)}, selectLast(event)], 
        span=1s
      )
    | countAs > 0
    | event = "B"

### Introduction

The [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function can be used to detect two events occurring in quick succession. 

In this example, the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function is used to detect event B occurring quickly after event A. 

Note that the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function must be used after an aggregator function to ensure event ordering. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

Example incoming data might look like this: 

@timestamp| event  
---|---  
1451606300500| A  
1451606301000| B  
1451606302000| A  
1451606304000| B  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | slidingTimeWindow(
             [{event = "A" | count(event, as=countAs)}, selectLast(event)], 
             span=1s
           )

Creates a sliding time window of 1 second. Within each window it counts the occurrences of event A, returning the results in a new field named countAs, and selects the event type of the last event in the window. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | countAs > 0

Filters for windows where at least one event A occurred. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3[/Filter/] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | event = "B"

Checks if the last event in the window is event B. 

  6. Event Result set.




### Summary and Results

The query is used to detect instances where event B occurs quickly (within 1 second) after event A. The [_`span`_](https://library.humio.com/data-analysis/functions-slidingtimewindow.html#query-functions-slidingtimewindow-span) parameter configures the interval, allowing this to be customized. 

Sample output from the incoming example data: 

countAs| event| @timestamp  
---|---|---  
1| B| 1451606301000  
  
The query is useful for identifying sequences of events that happen in quick succession, which could indicate specific patterns of behavior or system interactions.
