# Detect Continuously Upwards Going Trend | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-slidingwindow-neighbor-trend-detection.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Detect Continuously Upwards Going Trend

Detect continuously upwards going trend using the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function combined with [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} 4{{Aggregate}} 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result

logscale
    
    
    head()
    | neighbor(value, prefix=prev)
    | change := value - prev.value
    | slidingWindow(
        [
             {change >= 0 | count(as=positiveTrend)},
             {change < 0  | count(as=negativeTrend)}
        ],
        events=2
        )
    | positiveTrend >= 2

### Introduction

The [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function can be used to detect continuously upwards going trend. 

In this example, the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function combined with [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) is used to detect continuously upwards going trend. It looks for sequences where the value is consistently increasing or staying the same over at least two consecutive measurements. 

Note that sequence functions must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

value  
---  
3  
5.5  
4  
6  
10  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} 4{{Aggregate}} 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} 4{{Aggregate}} 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | neighbor(value, prefix=prev)

Creates a new field named prev.value containing the value from the previous event. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} 4{{Aggregate}} 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | change := value - prev.value

Calculates the change between the current value and the previous value, and assigns the returned results to a field named change. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} 4{{Aggregate}} 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | slidingWindow(
             [
                  {change >= 0 | count(as=positiveTrend)},
                  {change < 0  | count(as=negativeTrend)}
             ],
             events=2
             )

Creates a sliding window of 2 events. Within each window, it counts changes equal to zero or higher (positive or zero changes) and returns the results in a field named positiveTrend, and then also counts the negative changes and returns the results in a field named negativeTrend. 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{{Aggregate}} 4{{Aggregate}} 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | positiveTrend >= 2

Filters for windows where there are at least 2 positive (or zero) changes. 

  7. Event Result set.




### Summary and Results

The query is used to detect a continuous upwards trend in a series of values. The query can be used to monitor system metrics for consistent increases (for example, memory usage, CPU load) and to identify potential anomalies in time-series data. 

Sample output from the incoming example data: 

value| positiveTrend| negativeTrend| change| prev.value  
---|---|---|---|---  
10| 2| 0| 4| 6
