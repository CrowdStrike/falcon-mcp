# Filter For Items Not Part of Data Set Using !join()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-join-negated-set-difference.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter For Items Not Part of Data Set Using `!join()`

Find the set difference using the [`join()`](https://library.humio.com/data-analysis/functions-join.html) function with negation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    #repo=A session_id=*
    | !join(query={#repo=B session_id=*}, field=session_id, key=session_id)

### Introduction

The [`join()`](https://library.humio.com/data-analysis/functions-join.html) function can be used with a negation to filter for items that are not part of a data set, for example, items in data set A not found in data set B. 

In this example, the [`join()`](https://library.humio.com/data-analysis/functions-join.html) function is used with a negation to search and find all session IDs from data set A that are not found in data set B. 

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

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #repo=A session_id=*

Filters for all events from repository `A`, that have a session_id field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | !join(query={#repo=B session_id=*}, field=session_id, key=session_id)

Performs a negated join with repository `B`, and returns sessions that exist in repository `A` but not in repository `B`. The negation operator is used to make it an anti-join operation. 

LogScale recommends using the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function with `!match()` instead of negated join. See example [Filter For Items Not Part of Data Set Using `defineTable()` ](examples-definetable-negated-set-difference.html "Filter For Items Not Part of Data Set Using defineTable\(\)")

  4. Event Result set.




### Summary and Results

The query is used to find the set difference between two repositories. This is, for example, useful for identifying sync issues or performing data consistency checks. Or just to make a cross-repository comparison. 

For more information, see also [Query Joins and Lookups](https://library.humio.com/data-analysis/query-joins.html)

Sample output from the incoming example data: 

timestamp| session_id| user_name| action| status  
---|---|---|---|---  
2025-04-01T07:10:00Z| 123458| mike.jones| upload| failed  
2025-04-01T07:15:00Z| 123459| sara.wilson| login| success
