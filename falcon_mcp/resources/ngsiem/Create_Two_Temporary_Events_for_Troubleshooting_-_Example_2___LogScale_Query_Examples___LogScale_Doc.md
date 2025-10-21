# Create Two Temporary Events for Troubleshooting - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-createevents-parsejson.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Two Temporary Events for Troubleshooting - Example 2

Create two temporary events for testing or troubleshooting using the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function with [`parseJson()`](https://library.humio.com/data-analysis/functions-parsejson.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    createEvents(["{\"animal\":{\"kind\":\"dog\", \"weight\":7.0}}", "{\"animal\":{\"kind\":\"cat\", \"weight\":4.2}}"])
    | parseJson()

### Introduction

The [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function generates temporary events as part of the query. The function is ideal for generating sample data for testing or troubleshooting. 

In this example, the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function is combined with [`parseJson()`](https://library.humio.com/data-analysis/functions-parsejson.html) to parse @rawstring as JSON. 

Example incoming data might look like this: 

json
    
    
    [
    {"animal":{"kind":"dog", "weight":7.0}},
    {"animal":{"kind":"cat", "weight":4.2}}
    ]

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         createEvents(["{\"animal\":{\"kind\":\"dog\", \"weight\":7.0}}", "{\"animal\":{\"kind\":\"cat\", \"weight\":4.2}}"])

Creates two temporary events. An event with `dog` and an event with `cat`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseJson()

Parses specified fields as JSON. 

  4. Event Result set.




### Summary and Results

The query is used to create temporary events and parse the @rawstring as JSON. 

Sample output from the incoming example data: 

@timestamp| animal.kind| animal.weight  
---|---|---  
1733311547717| dog| 7.0  
1733311547717| cat| 4.2
