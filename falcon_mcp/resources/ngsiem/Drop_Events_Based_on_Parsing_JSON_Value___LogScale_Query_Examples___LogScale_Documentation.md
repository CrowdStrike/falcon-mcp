# Drop Events Based on Parsing JSON Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-dropevent-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Drop Events Based on Parsing JSON Value

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    case {
    @rawstring="#*"
    | dropEvent();
    * }

### Introduction

The [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function can be used both during queries and within the parser pipeline. Depending on usage, the function has different behavior. 

If used during parsing, the event is dropped and removed entirely from the query output, meaning that the event data will not be stored in LogScale. If used within normal searching, the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function is simply an alias for false - it behaves the same as `false`. 

When parsing incoming data, it is sometimes the case that the data includes 'commented' data, where,for example, the `#` character is used to identify comments in files rather than real data. This example removes those lines from the ingest process during parsing using the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function to drop the entire event from the ingest pipeline. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         case {
         @rawstring="#*"
         | dropEvent();

Starts a `case` statement, with the first matching expression looking for the hash symbol in a line to indicate that it could be removed, then dropping the entire event using [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html)

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         * }

For all other lines, the `case` expression matches all other events and lets them through. 

  4. Event Result set.




### Summary and Results

This query is used to remove data at ingestion, in this example data that matches a typical source construct (the comment). When used within the parser pipeline, the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function ensures that the data is removed entirely from the query output, meaning that the event data will not be stored in LogScale.
