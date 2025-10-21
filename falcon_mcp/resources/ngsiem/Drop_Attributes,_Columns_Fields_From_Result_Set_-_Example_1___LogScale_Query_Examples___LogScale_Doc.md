# Drop Attributes, Columns/Fields From Result Set - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-drop-header-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Drop Attributes, Columns/Fields From Result Set - Example 1

Drop a single field from a result set using the [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#2ac76d; click 1 #examples-drop-header-1-1

logscale
    
    
    drop(header)

### Introduction

The [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function is used to drop fields (remove attributes and columns) from result set. The function excludes a specified number of rows or columns from the start or end of an array. 

In this example, the [`drop()`](https://library.humio.com/data-analysis/functions-drop.html) function is used to remove the header field from result set. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Drop Field\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#2ac76d; click 1 #examples-drop-header-1-1 style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         drop(header)

Drops a single field named header. 

  3. Event Result set.




### Summary and Results

The query is used to remove data during ingest, in this example removing a field. Removal of fields are useful if you have created fields in sub-searches (extracted some values in new fields during the filtering process) that are no longer needed in the final result set. If you want to drop an entire event, it is possible to use the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function.
