# Calculate Sum of Field Values Over Sliding Time-Based Window | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-slidingtimewindow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Sum of Field Values Over Sliding Time-Based Window

Calculate a sum of values in a dataset over a sliding time-based window using the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    head()
    | slidingTimeWindow(sum(value), span=3s)

### Introduction

The [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function can be used to calculate metrics over a specific time period. The [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function analyzes data within a moving time frame and performs calculation on the data within that time period. As time progresses, it updates the calculations, always using the most recent time period. 

In this example, the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function is used with the [`head()`](https://library.humio.com/data-analysis/functions-head.html) function to calculate the sum of the field value over a sliding time-based window of 3 seconds. 

Note that the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function must be used after an aggregator function to ensure event ordering by time. Also note that the events must be sorted in order by timestamp to prevent errors when running the query. It is possible to select any field to use as a timestamp. 

Example incoming data might look like this: 

value| @timestamp  
---|---  
1| 1451606301001  
4| 1451606301002  
11| 1451606302400  
2| 1451606304001  
5| 1451606304003  
1| 1451606305300  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         head()

Selects the oldest events ordered by time. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | slidingTimeWindow(sum(value), span=3s)

Computes the running sum of the field value over a 3-second window using the [`slidingTimeWindow()`](https://library.humio.com/data-analysis/functions-slidingtimewindow.html) function with the [`sum()`](https://library.humio.com/data-analysis/functions-sum.html) aggregator. It adds the values of this 3-second window together and updates the sum as new data points arrive, always considering only the last 3 seconds. 

It is also possible to exclude the current value, if adding `current="exclude"`: `slidingTimeWindow(sum(value), span="3s", current="exclude")`

Note that it is possible to select any field to use as a timestamp, which can be useful after the bucket function. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the sum of fields over a sliding time-based window using a 3 second time window. The query is useful to identify trends in most recent data. 

Sample output from the incoming example data: 

_sum| @timestamp| value  
---|---|---  
1| 1451606301001| 1  
5| 1451606301002| 4  
16| 1451606302400| 11  
17| 1451606304001| 2  
18| 1451606304003| 5  
19| 1451606305300| 1  
  
Sample output from the incoming example data if the current event value is excluded: 

_sum| @timestamp| value  
---|---|---  
0| 1451606301001| 1  
1| 1451606301002| 4  
5| 1451606302400| 11  
15| 1451606304001| 2  
13| 1451606304003| 5  
18| 1451606305300| 1  
  
To analyze data based on a set number of data points instead of time periods, use the [`slidingWindow()`](https://library.humio.com/data-analysis/functions-slidingwindow.html) function.
