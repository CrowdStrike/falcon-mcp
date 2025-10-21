# Extract Year From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timeyear-extract-year.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Year From Timestamp

Get the year from a timestamp using the [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:year(timestamp, as=year)

### Introduction

The [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) function can be used to extract the year from a timestamp field. It returns the year as a four-digit integer value. 

In this example, the [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) function is used to extract the year from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the year value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:year(timestamp, as=year)

Extracts the year from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named year. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-year.html#query-functions-time-year-as) parameter is not specified, the result is returned in a field named _year as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the year from a timestamp, which is useful for analyzing events across different years. 

This query is useful, for example, to analyze yearly patterns, group events by year, or investigate long-term trends. 

Sample output from the incoming example data: 

@timestamp| year  
---|---  
2025-08-27 08:51:51.312| 2025  
  
The result shows how the [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) function extracts the year (in this case `2025`) from the timestamp. 

For visualizing this data, consider using a Bar Chart widget to show event distribution across years, or a Line Chart widget to display trends over multiple years. The [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) function is often used with other time functions like [`time:month()`](https://library.humio.com/data-analysis/functions-time-month.html) and [`time:dayOfYear()`](https://library.humio.com/data-analysis/functions-time-dayofyear.html) for complete date analysis.
