# Extract Hour From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timehour-extract-hour.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Hour From Timestamp

Get the hour from a timestamp using the [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:hour(timestamp, as=hour)

### Introduction

The [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function can be used to extract the hour (0-23) from a timestamp field. It returns the hour as an integer value using the 24-hour clock format. 

In this example, the [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function is used to extract the hour from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the hour value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:hour(timestamp, as=hour)

Extracts the hour from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named hour. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-hour.html#query-functions-time-hour-as) parameter is not specified, the result is returned in a field named _hour as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the hour from a timestamp, which is useful for analyzing event patterns throughout the day. 

This query is useful, for example, to analyze hourly patterns, identify peak activity hours, or group events by time of day. 

Sample output from the incoming example data: 

@timestamp| hour  
---|---  
2025-08-27 08:51:51.000| 8  
  
The result shows how the [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function extracts the hour (in this case `8`) from the timestamp, indicating it is 8 AM in 24-hour format. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across hours, or a Heat Map widget to display activity patterns throughout the day. The [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function is often used with other time functions like [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) and [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) for complete time analysis.
