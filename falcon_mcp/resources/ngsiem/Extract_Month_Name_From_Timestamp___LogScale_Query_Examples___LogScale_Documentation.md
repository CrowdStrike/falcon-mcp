# Extract Month Name From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timemonthname-extract-monthname.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Month Name From Timestamp

Get the name of the month from a timestamp using the [`time:monthName()`](https://library.humio.com/data-analysis/functions-time-monthname.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:monthName(timestamp, as=month)

### Introduction

The [`time:monthName()`](https://library.humio.com/data-analysis/functions-time-monthname.html) function can be used to extract the English name of the month from a timestamp field. It returns the full month name as a string value (January through December). 

In this example, the [`time:monthName()`](https://library.humio.com/data-analysis/functions-time-monthname.html) function is used to extract the month name from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the month name from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:monthName(timestamp, as=month)

Extracts the month name from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named month. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-monthname.html#query-functions-time-monthname-as) parameter is not specified, the result is returned in a field named _monthName as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the month name from a timestamp, which is useful for creating human-readable output and reports. 

This query is useful, for example, to generate readable reports, create user-friendly displays, or label data with month names. 

Sample output from the incoming example data: 

@timestamp| month  
---|---  
2025-08-27 08:51:51.312| August  
  
The result shows how the [`time:monthName()`](https://library.humio.com/data-analysis/functions-time-monthname.html) function extracts the month name (in this case `August`) from the timestamp, returning it as a string value. 

For visualizing this data, consider using a Bar Chart widget to show event counts by month name, or a Table widget to display events with their corresponding month names. The [`time:monthName()`](https://library.humio.com/data-analysis/functions-time-monthname.html) function is often used with other time functions like [`time:year()`](https://library.humio.com/data-analysis/functions-time-year.html) and [`time:dayOfMonth()`](https://library.humio.com/data-analysis/functions-time-dayofmonth.html) for complete date analysis.
