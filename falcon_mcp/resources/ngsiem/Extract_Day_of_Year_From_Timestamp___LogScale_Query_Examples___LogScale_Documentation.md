# Extract Day of Year From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timedayofyear-extract-yearday.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Day of Year From Timestamp

Get the day of year from a timestamp using the [`time:dayOfYear()`](https://library.humio.com/data-analysis/functions-time-dayofyear.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:dayOfYear(timestamp, as=yearday)

### Introduction

The [`time:dayOfYear()`](https://library.humio.com/data-analysis/functions-time-dayofyear.html) function can be used to extract the day of the year (1-365, or 366 in leap years) from a timestamp field. It returns the day as an integer value representing the number of days since the start of the year. 

In this example, the [`time:dayOfYear()`](https://library.humio.com/data-analysis/functions-time-dayofyear.html) function is used to extract the day from a specific timestamp `2025-08-27 08:51:51.000`, demonstrating how to get the day of year value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:dayOfYear(timestamp, as=yearday)

Extracts the day of the year from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named yearday. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-dayofyear.html#query-functions-time-dayofyear-as) parameter is not specified, the result is returned in a field named _dayOfYear as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the day of the year from a timestamp, which is useful for analyzing event patterns across the entire year. 

This query is useful, for example, to analyze annual patterns, track yearly progress, or identify seasonal trends. 

Sample output from the incoming example data: 

@timestamp| yearday  
---|---  
2025-08-27 08:51:51.000| 239  
  
The result shows how the [`time:dayOfYear()`](https://library.humio.com/data-analysis/functions-time-dayofyear.html) function extracts the day of the year (in this case `239`) from the timestamp, indicating it is the 239th day of 2025. 

For visualizing this data, consider using a Line Chart widget to show event patterns across the year, or a Heat Map widget to display activity patterns throughout the year. The [`time:dayOfYear()`](https://library.humio.com/data-analysis/functions-time-dayofyear.html) function is often used with other time functions like [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) and [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) for complete date analysis.
