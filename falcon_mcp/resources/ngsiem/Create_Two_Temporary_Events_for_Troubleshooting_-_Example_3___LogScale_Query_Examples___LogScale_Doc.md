# Create Two Temporary Events for Troubleshooting - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-createevents-kvparse.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Two Temporary Events for Troubleshooting - Example 3

Create two temporary events for testing or troubleshooting using the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function with [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])
    | kvParse()

### Introduction

The [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function generates temporary events as part of the query. The function is ideal for generating sample data for testing or troubleshooting. 

In this example, the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function is combined with [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) to parse @rawstring as JSON. 

Example incoming data might look like this: 

animal=dog weight=7.0  
---  
animal=cat weight=4.2  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])

Creates two temporary events. An event with `dog` and an event with `cat`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | kvParse()

Parses the string into key value pairs. 

  4. Event Result set.




### Summary and Results

The query is used to create temporary events and parse the @rawstring as key value pairs. 

Sample output from the incoming example data: 

animal| weight  
---|---  
dog| 7.0  
cat| 4.2
