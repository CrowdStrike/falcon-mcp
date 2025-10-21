# Extract Minute From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timeminute-extract-minute.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Minute From Timestamp

Get the minute from a timestamp using the [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:minute(timestamp, as=minute)

### Introduction

The [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) function can be used to extract the minute (0-59) from a timestamp field. It returns the minute as an integer value representing the minutes within the hour. 

In this example, the [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) function is used to extract the minute from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the minute value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:minute(timestamp, as=minute)

Extracts the minute from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named minute. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-minute.html#query-functions-time-minute-as) parameter is not specified, the result is returned in a field named _minute as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the minute from a timestamp, which is useful for analyzing events at a minute-level granularity. 

This query is useful, for example, to analyze per-minute patterns, group events by minute, or investigate timing patterns within hours. 

Sample output from the incoming example data: 

@timestamp| minute  
---|---  
2025-08-27 08:51:51.312| 51  
  
The result shows how the [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) function extracts the minute (in this case `51`) from the timestamp, indicating it is 51 minutes past the hour. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across minutes, or a Heat Map widget to display activity patterns within hours. The [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) function is often used with other time functions like [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) and [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) for detailed time analysis.
