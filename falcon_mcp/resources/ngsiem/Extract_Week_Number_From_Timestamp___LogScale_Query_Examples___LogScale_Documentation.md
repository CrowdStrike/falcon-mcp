# Extract Week Number From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timeweekofyear-extract-weeknumber.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Week Number From Timestamp

Get the ISO week number from a timestamp using the [`time:weekOfYear()`](https://library.humio.com/data-analysis/functions-time-weekofyear.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:weekOfYear(timestamp, as=week)

### Introduction

The [`time:weekOfYear()`](https://library.humio.com/data-analysis/functions-time-weekofyear.html) function can be used to extract the ISO week number (1-53) from a timestamp field. Following ISO 8601 standards, weeks start on Monday, and the first week of the year contains the year's first Thursday. 

In this example, the [`time:weekOfYear()`](https://library.humio.com/data-analysis/functions-time-weekofyear.html) function is used to extract the week number from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the ISO week value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:weekOfYear(timestamp, as=week)

Extracts the ISO week number from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named week. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-weekofyear.html#query-functions-time-weekofyear-as) parameter is not specified, the result is returned in a field named _weekOfYear as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the week number from a timestamp, which is useful for analyzing events at a weekly level following international standards. 

This query is useful, for example, to analyze weekly patterns, group events by ISO week, or investigate trends across weeks of the year. 

Sample output from the incoming example data: 

@timestamp| week  
---|---  
2025-08-27 08:51:51.312| 35  
  
The result shows how the [`time:weekOfYear()`](https://library.humio.com/data-analysis/functions-time-weekofyear.html) function extracts the week number (in this case `35`) from the timestamp, indicating it is the 35th week of 2025 according to ISO 8601 standards. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across weeks, or a Heat Map widget to display activity patterns throughout the year by week. The [`time:weekOfYear()`](https://library.humio.com/data-analysis/functions-time-weekofyear.html) function is often used with other time functions like [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) and [`time:dayOfWeek()`](https://library.humio.com/data-analysis/functions-time-dayofweek.html) for complete date analysis.
