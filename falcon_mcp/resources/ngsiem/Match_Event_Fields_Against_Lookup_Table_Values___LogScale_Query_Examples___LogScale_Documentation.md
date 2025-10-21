# Match Event Fields Against Lookup Table Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-match-id-value-column.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Match Event Fields Against Lookup Table Values

Compare event fields with column values in a lookup table using the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    match(file="users.csv", column=userid, field=id, include=[])

### Introduction

The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is useful for comparing or combining data from multiple sources. The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function allows searching and enriching data using CSV or JSON files, working as a filter or join operation in queries. 

In this example, the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is used to match the column userid of the `users.csv` file against the id field in the event. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         match(file="users.csv", column=userid, field=id, include=[])

Matches events for which the id field matches the value of the column userid in the `users.csv` file (the lookup table file). All events with non-matching IDs are filtered out. 

No additional columns are added. 

  3. Event Result set.




### Summary and Results

The query is used to compare and match event fields and file values as strings, in this case using exact string matching (the default value of the [_`mode`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-mode) parameter is `string`). The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is useful for comparing or combining data from multiple sources. In this example, only events with matching values are passed on, meaning that all events with non-matching IDs are removed. Matching events against an authorized users list is, for example, useful for filtering out unauthorized access attempts, for validation of user activities, or other monitoring.
