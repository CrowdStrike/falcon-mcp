# Extract Day of Month From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timedayofmonth-extract-day.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Day of Month From Timestamp

Get the day of month from a timestamp using the [`time:dayOfMonth()`](https://library.humio.com/data-analysis/functions-time-dayofmonth.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:dayOfMonth(timestamp, as=day)

### Introduction

The [`time:dayOfMonth()`](https://library.humio.com/data-analysis/functions-time-dayofmonth.html) function can be used to extract the day of the month (1-31) from a timestamp field. It returns the day as an integer value representing the date within the month. 

In this example, the [`time:dayOfMonth()`](https://library.humio.com/data-analysis/functions-time-dayofmonth.html) function is used to extract the day from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the day value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:dayOfMonth(timestamp, as=day)

Extracts the day of the month from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named day. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-dayofmonth.html#query-functions-time-dayofmonth-as) parameter is not specified, the result is returned in a field named _dayOfMonth as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the day of the month from a timestamp, which is useful for analyzing event patterns across different days within months. 

This query is useful, for example, to analyze daily patterns, group events by day, or identify activity trends within months. 

Sample output from the incoming example data: 

@timestamp| day  
---|---  
2025-08-27 08:51:51.000| 27  
  
The result shows how the [`time:dayOfMonth()`](https://library.humio.com/data-analysis/functions-time-dayofmonth.html) function extracts the day of the month (in this case `27`) from the timestamp, returning it as an integer value. 

For visualizing this data, consider using a Bar Chart widget to show event counts by day of month, or a Heat Map widget to display activity patterns across days. The [`time:dayOfMonth()`](https://library.humio.com/data-analysis/functions-time-dayofmonth.html) function is often used with other time functions like [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) and [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) for complete date analysis.
