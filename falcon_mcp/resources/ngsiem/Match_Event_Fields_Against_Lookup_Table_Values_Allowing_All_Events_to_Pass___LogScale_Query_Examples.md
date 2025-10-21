# Match Event Fields Against Lookup Table Values Allowing All Events to Pass | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-match-strict-false.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Match Event Fields Against Lookup Table Values Allowing All Events to Pass

Compare event fields with column values in lookup table using the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function with [_`strict`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-strict) parameter to allow also non-matching events to pass 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    id =~ match(file="users.csv", column=userid, strict=false)

### Introduction

The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is useful for comparing or combining data from multiple sources. The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function allows searching and enriching data using CSV or JSON files, working as a filter or join operation in queries. 

In this example, the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is used to match event IDs against the column userid of the `users.csv` file, adding the matching user details to the events. As the [_`strict`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-strict) parameter is set to `true`, all events - including non-matching events - are passed through, but only events with matches will be enriched with all other columns of the matching row. 

Example incoming event data might look like this: 

@timestamp| id| action| source_ip  
---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1  
2024-01-15T09:01:00.000Z| unknown-user| login_attempt| 10.0.0.2  
2024-01-15T09:02:00.000Z| dev-user-456| code_push| 10.0.0.3  
  
Example `users.csv` file data might look like this: 

userid| department| access_level| location  
---|---|---|---  
ADMIN-123| IT| administrator| HQ  
dev-user-456| Engineering| developer| Remote  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         id =~ match(file="users.csv", column=userid, strict=false)

When an event ID matches the column userid in the `users.csv` lookup file, all columns from that first matching row are added to the event. The column names become new field names. 

As the [_`strict`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-strict) parameter is set to `true`, all events - including non-matching events - are passed through, but only events with matches will be enriched with all other columns of the matching row. 

  3. Event Result set.




### Summary and Results

The query is used to enrich matching events while allowing all events to pass through. Matching events against an authorized users list is, for example, useful for filtering out unauthorized access attempts, for validation of user activities, or other monitoring. Showing non-matching events in output as well can, for example, be useful for tracking unauthorized access attempts, identifying unknown users or systems or for monitoring suspicious activities. 

Sample output from the incoming example data: 

@timestamp| id| action| source_ip| department| access_level| location  
---|---|---|---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1| IT| administrator| HQ  
2024-01-15T09:01:00.000Z| unknown-user| login_attempt| 10.0.0.2| <no value>| <no value>| <no value>  
2024-01-15T09:02:00.000Z| dev-user-456| code_push| 10.0.0.3| Engineering| developer| Remote  
  
After matching, the output combines original event fields with matched user details. Note how also non-matching events (in this example `unknown-user`) appear in output.
