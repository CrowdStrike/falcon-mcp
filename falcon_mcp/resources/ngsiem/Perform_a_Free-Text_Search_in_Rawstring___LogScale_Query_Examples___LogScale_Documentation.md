# Perform a Free-Text Search in Rawstring | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-createevents-rawstring-foo.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform a Free-Text Search in Rawstring

Perform a free-text search in a rawstring using the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    createEvents(["foobar"])|@rawstring="*foo*"

### Introduction

The [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function generates temporary events as part of the query and is ideal for generating sample data for testing or troubleshooting. 

In this example, the [`createEvents()`](https://library.humio.com/data-analysis/functions-createevents.html) function is used to do a free-text search for `foo`in a rawstring. The `*` around the value is to ensure, that we are looking for any value in @rawstring where `foo` is in the middle with any prefix or suffix. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         createEvents(["foobar"])|@rawstring="*foo*"

Free-text searches for `foo` in a rawstring. Notice that you must add `*` around the free text string `foo`. 

  3. Event Result set.




### Summary and Results

The query is used specifically to perform a free-text search in the @rawstring field. This can be useful in any case you may want to search a specific field name to check for that first part.
