# Create Two Temporary Events for Troubleshooting - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-createevents-testdata.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Two Temporary Events for Troubleshooting - Example 1

Create two temporary events for testing or troubleshooting using the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])

### Introduction

The [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function generates temporary events as part of the query. The function is ideal for generating sample data for testing or troubleshooting. 

Example incoming data might look like this: 

animal=dog weight=7.0  
---  
animal=cat weight=4.2  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])

Creates two temporary events to be used for testing purposes. An event with `dog` and an event with `cat`. 

  3. Event Result set.




### Summary and Results

The query is used to create temporary events. The [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function can be combined with different parsers to generate more interesting events, for example, with [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) or [`parseJson()`](https://library.humio.com/data-analysis/functions-parsejson.html). 

Sample output from the incoming example data: 

@rawstring| @timestamp| @timestamp.nanos  
---|---|---  
animal=dog weight=7.0| 1733310508872| 0  
animal=cat weight=4.2| 1733310508872| 0
