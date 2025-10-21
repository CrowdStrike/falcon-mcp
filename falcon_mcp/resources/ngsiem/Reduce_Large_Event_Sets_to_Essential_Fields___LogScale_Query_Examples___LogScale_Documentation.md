# Reduce Large Event Sets to Essential Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-select-http-get.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Reduce Large Event Sets to Essential Fields

Reduce large datasets to essential fields using the [`select()`](https://library.humio.com/data-analysis/functions-select.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    method=GET
    select([statuscode, responsetime])

### Introduction

The [`select()`](https://library.humio.com/data-analysis/functions-select.html) function can be used to specify a set of fields to select from each event and include in a resulting event set. 

The [`select()`](https://library.humio.com/data-analysis/functions-select.html) function reduces large event set to essential fields. The [`select()`](https://library.humio.com/data-analysis/functions-select.html) statement creates a table as default and copies data from one table to another. 

In this example, an unsorted table is selected for the statuscode field and the responsetime field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         method=GET

Filters for all HTTP request methods of the type `GET`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         select([statuscode, responsetime])

Creates an unsorted table showing the statuscode field and the responsetime field. 

  4. Event Result set.




### Summary and Results

The query is used to filter specific fields from an event set and create a table showing these fields (focused event set). In this example, the table shows the HTTP response status and the time taken to respond to the request which is useful for analyzing HTTP performance, monitoring response codes, and identifying slow requests.. The `select` function is useful when you want to export a few fields from a large number of events into a .CSV file without aggregating the values. For more information about export, see [Export Data](https://library.humio.com/data-analysis/searching-data-data-export.html). 

Note that whereas the LogScale UI can only show up to 200 events, the exported .CSV file contains all results. 

It is possible that an aggregate function, such as [`table()`](https://library.humio.com/data-analysis/functions-table.html) or [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) may be more suitable for summarizing and selecting the fields to be displayed.
