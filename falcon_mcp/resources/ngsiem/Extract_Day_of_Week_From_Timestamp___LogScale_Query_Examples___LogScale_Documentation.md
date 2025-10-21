# Extract Day of Week From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timedayofweek-extract-weekday.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Day of Week From Timestamp

Get the day of week from a timestamp using the [`time:dayOfWeek()`](https://library.humio.com/data-analysis/functions-time-dayofweek.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:dayOfWeek(timestamp, as=weekday)

### Introduction

The [`time:dayOfWeek()`](https://library.humio.com/data-analysis/functions-time-dayofweek.html) function can be used to extract the day of the week (1-7) from a timestamp field. It returns the day as an integer value where Monday is 1 and Sunday is 7. 

In this example, the [`time:dayOfWeek()`](https://library.humio.com/data-analysis/functions-time-dayofweek.html) function is used to extract the day from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the weekday value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:dayOfWeek(timestamp, as=weekday)

Extracts the day of the week from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named weekday. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-dayofweek.html#query-functions-time-dayofweek-as) parameter is not specified, the result is returned in a field named _dayOfWeek as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the day of the week from a timestamp, which is useful for analyzing event patterns across different days of the week. 

This query is useful, for example, to analyze weekly patterns, group events by weekday, or identify activity trends within weeks. 

Sample output from the incoming example data: 

@timestamp| weekday  
---|---  
2025-08-27 08:51:51.000| 3  
  
The result shows how the [`time:dayOfWeek()`](https://library.humio.com/data-analysis/functions-time-dayofweek.html) function extracts the day of the week (in this case `3`) from the timestamp, indicating that August 27, 2025, is a Wednesday. 

For visualizing this data, consider using a Bar Chart widget to show event counts by day of week, or a Heat Map widget to display activity patterns across weekdays. The [`time:dayOfWeek()`](https://library.humio.com/data-analysis/functions-time-dayofweek.html) function is often used with other time functions like [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) and [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) for complete date analysis.
