# Narrow the Search Interval | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-duration-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Narrow the Search Interval

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    test(@timestamp > now() - duration("2d"))

### Introduction

When searching across a range of timestamps, the ability to limit the search to a more specific range using a relative duration can limit the output. To achieve this with the search, make use of [`duration()`](https://library.humio.com/data-analysis/functions-duration.html) with a relative time, for example `2d` for two days and use this to compare against the current time and @timestamp of the event. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         test(@timestamp > now() - duration("2d"))

Creates a value based on a duration of `2d` (two days). This returns a value in milliseconds (`2 * 24 * 60 * 60 * 1000`). By subtracting the value from [`now()`](https://library.humio.com/data-analysis/functions-now.html) the value is two days ago from the time the event is executed. Then the value is compared to the @timestamp to filter the events. 

  3. Event Result set.




### Summary and Results

The result is syntactically equivalent to: 

logscale
    
    
    test(@timestamp > now() - 172800000)

As the value is in a human-readable and relative time syntax, the value can be used in dashboards and user-selected parameters.
