# Extract Second From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timesecond-extract-second.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Second From Timestamp

Get the second from a timestamp using the [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:second(timestamp, as=second)

### Introduction

The [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) function can be used to extract the second (0-59) from a timestamp field. It returns the seconds as an integer value representing the seconds within the minute. 

In this example, the [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) function is used to extract the seconds from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the second value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:second(timestamp, as=second)

Extracts the seconds from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named second. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-second.html#query-functions-time-second-as) parameter is not specified, the result is returned in a field named _second as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the seconds from a timestamp, which is useful for analyzing events at a second-level granularity. 

This query is useful, for example, to analyze per-second patterns, group events by second, or investigate timing patterns within minutes. 

Sample output from the incoming example data: 

@timestamp| second  
---|---  
2025-08-27 08:51:51.312| 51  
  
The result shows how the [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) function extracts the seconds (in this case `51`) from the timestamp, indicating it is 51 seconds into the minute. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across seconds, or a Heat Map widget to display activity patterns within minutes. The [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) function is often used with other time functions like [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) and [`time:millisecond()`](https://library.humio.com/data-analysis/functions-time-millisecond.html) for precise time analysis.
