# Hourly Data Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-events-hour.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Hourly Data Events

Summarize events by providing a count of the number of data events per hour using the [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    hr := time:hour(field="@ingesttimestamp")
    |groupBy(hr)

### Introduction

The [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function can be used to get the 24-hour clock of a given timestamp field. 

In this example, the [`time:hour()`](https://library.humio.com/data-analysis/functions-time-hour.html) function is used with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) to average the count of data events per hour. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         hr := time:hour(field="@ingesttimestamp")

Gets the hour (24-hour clock) of the values in the @ingesttimestamp and returns the results in a new field named `hr`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         |groupBy(hr)

Groups the returned results by hr field and provides a count of the number of data events per hour in a _count field. 

  4. Event Result set.




### Summary and Results

The query is used to average the count of data events per hour. The results can be plotted onto a bar chart.
