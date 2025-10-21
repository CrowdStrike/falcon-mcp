# Filter For Items Not Part of Data Set Using defineTable()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-definetable-negated-set-difference.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter For Items Not Part of Data Set Using [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html)

Find the set difference using the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function with `!match()`

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    defineTable(
    name=session_ids,
    query={#repo=B session_id=*},
    include=session_id
    )
    #repo=A session_id=*
    | !match(table=session_ids, field=session_id)

### Introduction

The [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function can be used with a `!match()` to filter for items that are not part of a data set, for example, items in data set A not found in data set B. 

In this example, the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function is used with a `!match()` to search and find all session IDs from data set A that are not found in data set B. 

![](images/venn-seta-not-setb.png)  
---  
  
Example incoming data from repository A might look like this: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:00:00Z| 123456| john.doe| login| success  
2025-04-01T07:05:00Z| 123457| jane.smith| download| success  
2025-04-01T07:10:00Z| 123458| mike.jones| upload| failed  
2025-04-01T07:15:00Z| 123459| sara.wilson| login| success  
2025-04-01T07:20:00Z| 123460| bob.brown| logout| success  
  
Example incoming data from repository B might look like this: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:00:00Z| 123456| john.doe| login| success  
2025-04-01T07:05:00Z| 123457| jane.smith| download| success  
2025-04-01T07:20:00Z| 123460| bob.brown| logout| success  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         defineTable(
         name=session_ids,
         query={#repo=B session_id=*},
         include=session_id
         )

Generates an ad-hoc table from repository `B` named `session_ids` and filters on all events in repository `B` that contain the field session_id. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #repo=A session_id=*

Filters for all events from repository `A`, that contain a session_id field. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2["Expression"] 3["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | !match(table=session_ids, field=session_id)

Performs a negated match with repository `B`, and returns sessions that exist in repository `A` but not in repository `B`. The negation operator is used to return non-matching results. 

  5. Event Result set.




### Summary and Results

The query is used to find the set difference between two repositories. This is, for example, useful for identifying sync issues or performing data consistency checks. Or just to make a cross-repository comparison. 

For more information, see also [Query Joins and Lookups](https://library.humio.com/data-analysis/query-joins.html)

Sample output from the incoming example data: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:10:00Z| 123458| mike.jones| upload| failed  
2025-04-01T07:15:00Z| 123459| sara.wilson| login| success
