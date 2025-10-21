# Set Time Interval From Within Query with defineTable()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-settimeinterval-definetable.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set Time Interval From Within Query with [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html)

Set the time interval and related metadata from within the query instead of through the test QueryJobs API or UI using the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] 2@{ shape: win-pane, label: "Table" } 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    setTimeInterval(start="1h", end="30min")
    | defineTable(
    start=7d,
    end=1d,
    query={...},
    name="ended_queries")
    | match(table="ended_queries", field=queryID, strict=true)

### Introduction

The [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function can be used to set the time interval and related metadata from within the query instead of through the [QueryJobs API](https://library.humio.com/logscale-api/api-search-query-create.html) or the UI. The time settings of the [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function will overwrite whatever was specified in the QueryJobs API or UI. [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) must appear in the preamble of the query, before any other functions, filters, free-text searches, etc. It cannot appear inside [`join()`](https://library.humio.com/data-analysis/functions-join.html)/[`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) subqueries. 

In this example, the [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function is used with the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function to define a new time interval for the subqueries, before running this. 

Note that the [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function must appear before any [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) definitions and only one time in a query. 

For more information about time specification options, see [Search API Time Specification](https://library.humio.com/logscale-api/api-search-timespec.html). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] 2@{ shape: win-pane, label: "Table" } 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         setTimeInterval(start="1h", end="30min")

Recalls the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) subquery time interval. This means that the subquery will start at `7d+30min`, and will end at `1d+30min`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] 2@{ shape: win-pane, label: "Table" } 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | defineTable(
         start=7d,
         end=1d,
         query={...},
         name="ended_queries")

Generates an ad-hoc table named `ended_queries` and computes the relative time points to the primary query's time end time. This means that the subquery will start at `7d+30min`, and will end at `1d+30min`

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] 2@{ shape: win-pane, label: "Table" } 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | match(table="ended_queries", field=queryID, strict=true)

Joins the filtered events where the value equals `queryID` with the ended_queries table. 

  5. Event Result set.




### Summary and Results

This query demonstrates how to use [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) to define the timespan for a defined table query.
