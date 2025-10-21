# Bucket Events Summarized by count()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-buckets-count.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Bucket Events Summarized by [`count()`](https://library.humio.com/data-analysis/functions-count.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    bucket(function=count())

### Introduction

Divides the search time interval into buckets. As time span is not specified, the search interval is divided into 127 buckets. Events in each bucket are counted: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         bucket(function=count())

Summarizes events using the [`count()`](https://library.humio.com/data-analysis/functions-count.html) into buckets across the selected timespan. 

  3. Event Result set.




### Summary and Results

This query organizes data into buckets according to the count of events.
