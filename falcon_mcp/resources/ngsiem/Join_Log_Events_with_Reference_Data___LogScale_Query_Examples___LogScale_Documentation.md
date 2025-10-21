# Join Log Events with Reference Data | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-join-inner-logs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Join Log Events with Reference Data

Combining events from different queries using the [`join()`](https://library.humio.com/data-analysis/functions-join.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2@{ shape: processes, label: "Join" } result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    event_type=auth
    join({repo=user_details}, field=department, key=user_id, mode=inner)

### Introduction

The [`join()`](https://library.humio.com/data-analysis/functions-join.html) function can be used to combine events from two different queries based on matching field values. This is useful for enriching events with additional context from another data source. 

In this example, the [`join()`](https://library.humio.com/data-analysis/functions-join.html) function is used to combine authentication events with user details from a reference repository. 

Example incoming data might look like this: 

@timestamp| event_type| user_id| action| status  
---|---|---|---|---  
2025-09-01T10:00:00Z| auth| U123| login| success  
2025-09-01T10:00:05Z| auth| U456| login| failed  
2025-09-01T10:00:10Z| auth| U789| password_change| success  
2025-09-01T10:00:15Z| auth| U123| logout| success  
2025-09-01T10:00:20Z| auth| U456| login| failed  
2025-09-01T10:00:25Z| auth| U789| login| success  
2025-09-01T10:00:30Z| auth| U123| login| success  
2025-09-01T10:00:35Z| auth| U999| login| failed  
2025-09-01T10:00:40Z| auth| U456| password_reset| success  
2025-09-01T10:00:45Z| auth| U123| logout| success  
  
And the reference data in the `user_details` repository looks like this: 

@timestamp| user_id| department| role| location  
---|---|---|---|---  
2025-09-01T00:00:00Z| U123| IT| admin| London  
2025-09-01T00:00:00Z| U456| Sales| user| Paris  
2025-09-01T00:00:00Z| U789| HR| manager| Berlin  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2@{ shape: processes, label: "Join" } result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         event_type=auth

Filters the primary query to include only authentication events where event_type equals `auth`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2@{ shape: processes, label: "Join" } result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         join({repo=user_details}, field=department, key=user_id, mode=inner)

Performs an inner join with the `user_details` repository. The join: 

     * Uses [_`repo`_](https://library.humio.com/data-analysis/functions-join.html#query-functions-join-repo)=`user_details` to specify the repository containing reference data. 

     * Uses [_`field`_](https://library.humio.com/data-analysis/functions-join.html#query-functions-join-field)=`department` to specify which field to include from the reference data. 

     * Uses [_`key`_](https://library.humio.com/data-analysis/functions-join.html#query-functions-join-key)=`user_id` to specify the field to join on. 

     * Uses [_`mode`_](https://library.humio.com/data-analysis/functions-join.html#query-functions-join-mode)=`inner` to only include events where there is a match in both datasets. 

  4. Event Result set.




### Summary and Results

The query is used to enrich authentication events with user department information from a reference repository. 

This query is useful, for example, to analyze authentication patterns by department or to investigate security incidents with additional user context. 

Sample output from the incoming example data: 

@timestamp| event_type| user_id| action| status| department  
---|---|---|---|---|---  
2025-09-01T10:00:00Z| auth| U123| login| success| IT  
2025-09-01T10:00:05Z| auth| U456| login| failed| Sales  
2025-09-01T10:00:10Z| auth| U789| password_change| success| HR  
2025-09-01T10:00:15Z| auth| U123| logout| success| IT  
2025-09-01T10:00:20Z| auth| U456| login| failed| Sales  
2025-09-01T10:00:25Z| auth| U789| login| success| HR  
2025-09-01T10:00:30Z| auth| U123| login| success| IT  
2025-09-01T10:00:40Z| auth| U456| password_reset| success| Sales  
2025-09-01T10:00:45Z| auth| U123| logout| success| IT  
  
Note that the event with user_id=`U999` is not included in the output because it has no matching record in the reference data (inner join behavior). 

For other [`join()`](https://library.humio.com/data-analysis/functions-join.html) examples, see also [`join()` Syntax](https://library.humio.com/data-analysis/query-joins-methods-join.html#query-joins-methods-join-syntax).
