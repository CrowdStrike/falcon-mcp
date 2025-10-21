# Track Event Size Within a Repository | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-event-size-track.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Track Event Size Within a Repository

Calculate the event size and report the relative size statistics for each event using [`eventSize()`](https://library.humio.com/data-analysis/functions-eventsize.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    eventSize(as=eventSize)
    |timeChart(function=[max(eventSize),percentile(field=eventSize,percentiles=[50,75,90,99])])

### Introduction

The [`eventSize()`](https://library.humio.com/data-analysis/functions-eventsize.html) function is used to search for events depending on the internal disk storage usages. The function augments the event data with the event size information. 

This query shows how statistical information about events can first be determined, and then converted into a graph that shows the relative sizes. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         eventSize(as=eventSize)

Extracts the information about the size of each individual event using the [`eventSize()`](https://library.humio.com/data-analysis/functions-eventsize.html) function. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         |timeChart(function=[max(eventSize),percentile(field=eventSize,percentiles=[50,75,90,99])])

Calculates the [`percentile()`](https://library.humio.com/data-analysis/functions-percentile.html) for the eventSize field and determines which filesize is above 50%,75%, and 90,99% of the overall event set, then finds the maximum size for the specified field over a set of events, and displays the returned results in a timechart. 

  4. Event Result set.




### Summary and Results

The query is used to show how statistical information about events can first be determined, and then converted into a graph that shows the relative sizes.
