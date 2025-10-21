# Sample Event Streams - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-sample-events-percentage.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Sample Event Streams - Example 1

Sample events keeping only specified percentage of the events using the [`sample()`](https://library.humio.com/data-analysis/functions-sample.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00;

logscale
    
    
    sample(percentage=2)

### Introduction

Event sampling can be used to determine the characteristics of a large set of data without processing every event. In this example, the [`sample()`](https://library.humio.com/data-analysis/functions-sample.html) function is used to keep `2%` of the events. If used as part of a query, these randomly selected events are passed to the next stage of the query. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sample(percentage=2)

Samples events keeping only `2%` of the events. 

  3. Event Result set.




### Summary and Results

The query is used to sample events keeping only specified percentage of the events. Event sampling can be used to determine the characteristics of a large set of data without processing every event. Sampling is useful in, for example, survey analysis making it possible to draw conclusions without surveying all events. Sampling can also be used to filter on both frequently and infrequently occurring events.
