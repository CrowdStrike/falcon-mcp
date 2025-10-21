# Search For Events by Number of Fields in Repository
     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-eventfieldcount-number.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search For Events by Number of Fields in Repository 

Search for events with a certain number of fields in a repository using [`eventFieldCount()`](https://library.humio.com/data-analysis/functions-eventfieldcount.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    eventFieldCount()
    | _eventFieldCount <  6

### Introduction

The [`eventFieldCount()`](https://library.humio.com/data-analysis/functions-eventfieldcount.html) function is used to search for events depending on the number of fields on the event. The [`eventFieldCount()`](https://library.humio.com/data-analysis/functions-eventfieldcount.html) function augments the event data with the event field count information. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         eventFieldCount()

Determines the number of fields that events has, and returns the results in a field named _eventFieldCount. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | _eventFieldCount <  6

Searches for events that has fewer than 6 fields. Notice that you cannot do a direct comparison, as the function augments the event data with the event field count information, rather than returning data. 

  4. Event Result set.




### Summary and Results

The query is used to get an overview of the event with a low field count.
