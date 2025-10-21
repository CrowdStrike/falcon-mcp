# Sample Event Streams - example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-sample-events-sort.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Sample Event Streams - example 2

Sample events keeping only specified percentage of the events and sort by host using the [`sample()`](https://library.humio.com/data-analysis/functions-sample.html) function with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) and [`sort()`](https://library.humio.com/data-analysis/functions-sort.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ffbf00;

logscale
    
    
    sample(percentage=0.1)
    | groupBy(host)
    | sort()

### Introduction

Event sampling can be used to determine the characteristics of a large set of data without processing every event. In this example, the [`sample()`](https://library.humio.com/data-analysis/functions-sample.html) function is used to keep `0.1%` of the events and find the most common hosts among the sampled events. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sample(percentage=0.1)

Samples events keeping only `0.1%` of the events. These randomly selected events are passed to the next stage of the query. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ffbf00; style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(host)

Groups the sampled events by the host field. 

The advantage of sampling events before grouping them is, that it allows for analysis of common patterns without hitting [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) limits. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ffbf00; style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | sort()

Sorts the returned results by their host to find the most common host (by default, in descending order of count). 

  5. Event Result set.




### Summary and Results

The query is used to sample events keeping only specified percentage of the events, and then find the most common host among the sampled events. Event sampling can be used to determine the characteristics of a large set of data without processing every event. Sampling is useful in for example survey analysis making it possible to draw conclusions without surveying all events. Sampling can also be used to filter on both frequently and infrequently occurring events.
