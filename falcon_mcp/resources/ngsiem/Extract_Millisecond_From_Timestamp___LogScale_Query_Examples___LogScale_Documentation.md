# Extract Millisecond From Timestamp | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timemillisecond-extract-millisecond.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Millisecond From Timestamp

Get the millisecond from a timestamp using the [`time:millisecond()`](https://library.humio.com/data-analysis/functions-time-millisecond.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    time:millisecond(timestamp, as=ms)

### Introduction

The [`time:millisecond()`](https://library.humio.com/data-analysis/functions-time-millisecond.html) function can be used to extract the millisecond (0-999) from a timestamp field. It returns the milliseconds as an integer value representing the fractional part of the second. 

In this example, the [`time:millisecond()`](https://library.humio.com/data-analysis/functions-time-millisecond.html) function is used to extract the milliseconds from a specific timestamp `2025-08-27 08:51:51.312`, demonstrating how to get the millisecond value from a datetime. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         time:millisecond(timestamp, as=ms)

Extracts the milliseconds from the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field and returns the result in a new field named ms. If the [_`as`_](https://library.humio.com/data-analysis/functions-time-millisecond.html#query-functions-time-millisecond-as) parameter is not specified, the result is returned in a field named _millisecond as default. 

  3. Event Result set.




### Summary and Results

The query is used to extract the milliseconds from a timestamp, which is useful for analyzing events at a sub-second level of precision. 

This query is useful, for example, to analyze high-precision timing, measure small time differences, or investigate event sequencing at millisecond resolution. 

Sample output from the incoming example data: 

@timestamp| ms  
---|---  
2025-08-27 08:51:51.312| 312  
  
The result shows how the [`time:millisecond()`](https://library.humio.com/data-analysis/functions-time-millisecond.html) function extracts the milliseconds (in this case `312`) from the timestamp, indicating there are 312 milliseconds in this timestamp. 

For visualizing this data, consider using a Scatter Plot widget to show event distribution within seconds, or a Line Chart widget to display high-precision timing patterns. The [`time:millisecond()`](https://library.humio.com/data-analysis/functions-time-millisecond.html) function is often used with other time functions like [`time:second()`](https://library.humio.com/data-analysis/functions-time-second.html) and [`time:minute()`](https://library.humio.com/data-analysis/functions-time-minute.html) for precise time analysis.
