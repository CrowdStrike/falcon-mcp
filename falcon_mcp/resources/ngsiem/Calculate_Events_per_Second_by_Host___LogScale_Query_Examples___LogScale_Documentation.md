# Calculate Events per Second by Host | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-events-per-second-each-host.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Events per Second by Host

Determine event rate for each host over a 5-minute period using an embedded expression within the` groupBy()` function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(host, function=[{count() | esp:=_count/300}])

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to group events by a field and perform calculations on each group, including derived metrics such as events per second. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used with an embedded expression to calculate the total event count and events per second for each host over a 5-minute period. 

Example incoming data might look like this: 

@timestamp| host| service| status| response_time  
---|---|---|---|---  
2025-08-06T10:00:00Z| server1| web| ok| 120  
2025-08-06T10:00:01Z| server2| database| ok| 85  
2025-08-06T10:00:02Z| server1| web| ok| 95  
2025-08-06T10:00:03Z| server3| cache| ok| 45  
2025-08-06T10:00:04Z| server2| database| error| 250  
2025-08-06T10:00:05Z| server1| web| ok| 110  
2025-08-06T10:00:06Z| server3| cache| ok| 40  
2025-08-06T10:00:07Z| server2| database| ok| 90  
2025-08-06T10:00:08Z| server1| web| error| 300  
2025-08-06T10:00:09Z| server3| cache| ok| 42  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(host, function=[{count() | esp:=_count/300}])

Groups events by the host field and uses an embedded expression to count the number of events per host and calculate events per second in one operation. 

The [`count()`](https://library.humio.com/data-analysis/functions-count.html) function returns the count in a field named _count by default. The embedded expression then divides this value by `300` and stores the result in a new field named esp. This calculation provides the average events per second for each host over the time period. 

Using an embedded expression within the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function performs both the count and the calculation as part of the same aggregation. Both the original _count and the calculated esp field are included in the results. 

  3. Event Result set.




### Summary and Results

The query is used to analyze event frequency patterns by calculating both the total event count and the average events per second for each host. 

Note that the query aggregates against both the original count and the count/300 as one aggregate set. Using an embedded expression is more efficient for larger event sets. 

This query is useful, for example, to monitor system load distribution across hosts, identify hosts with unusual event rates, or establish baseline activity patterns for capacity planning. 

Sample output from the incoming example data: 

host| _count| esp  
---|---|---  
server1| 4| 0.013333  
server2| 3| 0.010000  
server3| 3| 0.010000  
  
Note that the _count field shows the total number of events per host, and the esp field shows the calculated events per second (total events divided by 300 seconds) 

This data is ideal for visualization using a Time Chart widget to show event rates over time. A Bar Chart widget could compare event rates across hosts, while a Gauge widget could show current event rates against predefined thresholds. Consider creating a dashboard that combines these visualizations with alerts for when event rates exceed normal ranges.
