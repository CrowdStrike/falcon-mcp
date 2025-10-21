# Extract Day of Week Name From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timedayofweekname-extract-weekday.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Day of Week Name From Timestamp

Get the name of the weekday from a timestamp using the [`time:dayOfWeekName()`](https://library.humio.com/data-analysis/functions-time-dayofweekname.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:dayOfWeekName(timestamp, as=weekday)

### Introduction

The [`time:dayOfWeekName()`](https://library.humio.com/data-analysis/functions-time-dayofweekname.html) function can be used to extract the English name of the weekday from a timestamp field. It returns the full name of the day (Monday through Sunday) as a string value. 

In this example, the [`time:dayOfWeekName()`](https://library.humio.com/data-analysis/functions-time-dayofweekname.html) function is used to extract the weekday name from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the day name from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:dayOfWeekName(timestamp, as=weekday)

Extracts the name of the weekday from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named weekday. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-dayofweekname.html#query-functions-time-dayofweekname-as) parameter is not specified, the result is returned in a field named _dayOfWeekName as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the weekday name from a timestamp, which is useful for creating human-readable output and reports. 

This query is useful, for example, to generate readable reports, create user-friendly displays, or label data with weekday names. 

Sample output from the incoming example data: 

@timestamp| weekday  
---|---  
2025-08-27 08:51:51.000| Wednesday  
  
The result shows how the [`time:dayOfWeekName()`](https://library.humio.com/data-analysis/functions-time-dayofweekname.html) function extracts the day name (in this case `Wednesday`) from the timestamp, returning it as a string value. 

For visualizing this data, consider using a Bar Chart widget to show event counts by day name, or a Table widget to display events with their corresponding weekday names. The [`time:dayOfWeekName()`](https://library.humio.com/data-analysis/functions-time-dayofweekname.html) function is often used with other time functions like [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) and [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) for complete date analysis.
