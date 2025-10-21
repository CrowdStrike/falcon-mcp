# Extract Month From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timemonth-extract-month.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Month From Timestamp

Get the month from a timestamp using the [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:month(timestamp, as=month)

### Introduction

The [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) function can be used to extract the month (1-12) from a timestamp field. It returns the month as an integer value where January is 1 and December is 12. 

In this example, the [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) function is used to extract the month from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the month value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:month(timestamp, as=month)

Extracts the month from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named month. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-month.html#query-functions-time-month-as) parameter is not specified, the result is returned in a field named _month as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the month from a timestamp, which is useful for analyzing events at a monthly level. 

This query is useful, for example, to analyze monthly patterns, group events by month, or investigate seasonal trends throughout the year. 

Sample output from the incoming example data: 

@timestamp| month  
---|---  
2025-08-27 08:51:51.312| 8  
  
The result shows how the [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) function extracts the month (in this case `8`) from the timestamp, indicating August (the eighth month of the year). 

For visualizing this data, consider using a Bar Chart widget to show event distribution across months, or a Heat Map widget to display activity patterns throughout the year. The [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) function is often used with other time functions like [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) and [`time:dayOfMonth()`](https://library.humio.com/data-analysis/functions-time-dayofmonth.html) for complete date analysis.
