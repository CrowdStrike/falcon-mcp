# Search for Events by Size in Repository | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-eventsize-certain-size.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search for Events by Size in Repository

Search for events of a certain size in a repository using [`eventSize()`](https://library.humio.com/data-analysis/functions-eventsize.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    eventSize()
    | _eventSize > 10000

### Introduction

The [`eventSize()`](https://library.humio.com/data-analysis/functions-eventsize.html) function is used to search for events depending on the internal disk storage usages. The function augments the event data with the event size information. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         eventSize()

Determines the number of bytes that events internally use in disk storage for the values (not counting the bytes for storing the field names), and returns the results in a field named _eventSize. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | _eventSize > 10000

Searches for events that take up more than 10000 bytes in internal disk storage usage. Notice that you cannot do a direct comparison, as the function augments the event data with the event size information, rather than returning data. 

  4. Event Result set.




### Summary and Results

The query is used to get an overview of the disk storage usage of the different events and in this example filter on the largest ones. A high disk storage usage can cause performance issues, depending on the time range.
