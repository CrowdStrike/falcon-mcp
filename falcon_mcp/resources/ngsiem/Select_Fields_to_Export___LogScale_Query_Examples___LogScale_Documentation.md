# Select Fields to Export | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-select-rawstring.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Select Fields to Export

Select fields to export as .CSV file using the [`select()`](https://library.humio.com/data-analysis/functions-select.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    select([@timestamp, @rawstring])

### Introduction

The [`select()`](https://library.humio.com/data-analysis/functions-select.html) function can be used to specify a set of fields to select from each event and include in a resulting event set. 

The [`select()`](https://library.humio.com/data-analysis/functions-select.html) function reduces large event set to essential fields. The [`select()`](https://library.humio.com/data-analysis/functions-select.html) statement creates a table as default and copies data from one table to another. 

In this example, an unsorted table is selected for the @timestamp field and the @rawstring field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         select([@timestamp, @rawstring])

Creates an unsorted table showing the @timestamp field and the @rawstring field. 

  3. Event Result set.




### Summary and Results

The query is used to filter specific fields from an event set and create a table showing these fields (focused event set). In this example, the table shows the timestamp of the events and the complete raw log entry, which is useful for full log analysis, and data backup. The `select` function is useful when you want to export a few fields from a large number of events into a .CSV file without aggregating the values. For more information about export, see [Export Data](https://library.humio.com/data-analysis/searching-data-data-export.html). 

Note that whereas the LogScale UI can only show up to 200 events, an exported .CSV file contains all results.
