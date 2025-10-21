# Set Relative Time Interval From Within Query | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-settimeinterval-basic.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set Relative Time Interval From Within Query

Set the relative time interval and related metadata from within the query instead of through the QueryJobs API or UI 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    setTimeInterval(start=7d, end=1d)

### Introduction

The [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function can be used to set the time interval and related metadata from within the query instead of through the QueryJobs API or UI. The time settings of the [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function will overwrite whatever was specified in the QueryJobs API or UI. [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) must appear in the preamble of the query, before any other functions, filters, free-text searches, etc. 

In this example, the [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function is used to define a new relative time interval before running an ad-hoc query. 

For more information about time specification options, see [Search API Time Specification](https://library.humio.com/logscale-api/api-search-timespec.html). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         setTimeInterval(start=7d, end=1d)

Sets a time interval to start 7 days ago from now and to end 1 day ago from now. As the timezone is not specified, it uses the system's default. 

It is possible to explicitly set a timezone instead of using the system's default, in this example, the timezone is explicitly set to `Europe/Copenhagen`: `setTimeInterval(start="1w@d", end="now@d", timezone="Europe/Copenhagen")`

  3. Event Result set.




### Summary and Results

This query demonstrates how to use [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) to define the timespan from within the query instead of through the QueryJobs API or UI. 

For an example of using absolute time, see [Set Specific Time Interval Based on Raw Epoch Timestamps From Within Query](examples-settimeinterval-specify-time-range.html "Set Specific Time Interval Based on Raw Epoch Timestamps From Within Query").
