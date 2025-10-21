# Calculate Sum of Field Values Over Sliding Window | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-slidingwindow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Sum of Field Values Over Sliding Window

Calculate a sum of values in a dataset over a sliding window of a number of events using the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | slidingWindow(sum(value), events=3)

### Introduction

The [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function can be used to calculate cumulative metrics over a fixed number of recent events, allowing for trend analysis and smoothing of data. The [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function applies an aggregation function to a moving window of a specified number of events in a sequence. As new data arrives, the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function adds the newest data point to its analysis and removes the oldest data point from its analysis, recalculating results based on this updated set of data points. 

In this example, the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function is used with the [`sum()`](https://library.humio.com/data-analysis/functions-sum.html) function to calculate the sum of the field value over a sliding window of 3 events. 

Note that the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function must be used after an aggregator function to ensure event ordering. 

Example incoming data might look like this: 

value  
---  
1  
4  
11  
2  
5  
1  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | slidingWindow(sum(value), events=3)

Computes the running sum of the field value in the three most recent events using the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function with the [`sum()`](https://library.humio.com/data-analysis/functions-sum.html) aggregator. It adds the values of these three data points together and updates the calculation as new data points arrive, always using the latest three. It is also possible to exclude the current value, if adding `current="exclude"`: ` slidingWindow(sum(value), events=3, current="exclude")`

  4. Event Result set.




### Summary and Results

This query calculates the sum of fields over a sliding window of events. The query is useful to identify trends in most recent data. 

Sample output from the incoming example data: 

_sum| value  
---|---  
1| 1  
5| 4  
16| 11  
17| 2  
18| 5  
8| 1  
  
Sample output from the incoming example data if excluded: 

_sum| value  
---|---  
0| 1  
1| 4  
5| 11  
16| 2  
17| 5  
18| 1  
  
You could, for example, use [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) to calculate the average response time for the last 100 customer service requests, updating this average as each new request comes in. To analyze data based on time periods instead of a set number of data points, use the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function.
