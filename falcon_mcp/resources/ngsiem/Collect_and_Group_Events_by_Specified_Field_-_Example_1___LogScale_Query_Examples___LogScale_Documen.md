# Collect and Group Events by Specified Field - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-collect-urls.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Collect and Group Events by Specified Field - Example 1

Collect and group events by specified field using [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) as part of a [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) operation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(client_ip, function=session(maxpause=1m, collect([url])))

### Introduction

The [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) function can be used to collect fields from multiple events into one event as part of a [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) operation. The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to group together events by one or more specified fields. It is used to extract additional aggregations from the data and then add calculation to it using the [`count()`](https://library.humio.com/data-analysis/functions-count.html)function. 

In this example, the [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) function is used to collect visitors, each visitor defined as non-active after one minute. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(client_ip, function=session(maxpause=1m, collect([url])))

Collects visitors (URLs), each visitor defined as non-active after one minute and returns the results in an array named client_ip. A count of the events is returned in a _count field. 

  3. Event Result set.




### Summary and Results

The query is used to collect fields from multiple events into one event. This query analyzes user behavior by grouping events into sessions for each unique client IP address. It then collects all URLs accessed during each session. Collecting should be used on smaller data sets to create a list (or set, or map, or whatever) when you actually need a list object explicitly (for example, in order to pass it on to some other API). This analysis is valuable for understanding user engagement, and identifying potential security issues based on unusual browsing patterns. Using [`collect()`](https://library.humio.com/data-analysis/functions-collect.html) on larger data set may cause out of memory as it returns the entire data set.
