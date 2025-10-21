# Match Event Fields Against Patterns in Lookup Table Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-match-glob-pattern.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Match Event Fields Against Patterns in Lookup Table Values

Compare event fields with column values containing patterns in a lookup table using the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function with glob pattern matching 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    id =~ match(file="users.csv", column=userid, mode=glob, ignoreCase=true)

### Introduction

The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is useful for comparing or combining data from multiple sources. The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function allows searching and enriching data using CSV or JSON files, working as a filter or join operation in queries. 

In this example, the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is used with glob pattern matching (defined by the [_`mode`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-mode) parameter) to match event IDs against the column userid of the `users.csv` file, adding the matching user details to the events. 

Example incoming event data might look like this: 

@timestamp| id| action| source_ip  
---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1  
2024-01-15T09:01:00.000Z| dev-user-456| code_push| 10.0.0.2  
2024-01-15T09:02:00.000Z| TEST_789| test_run| 10.0.0.3  
2024-01-15T09:03:00.000Z| support-001| ticket_update| 10.0.0.4  
2024-01-15T09:04:00.000Z| unknown-user| login_attempt| 10.0.0.5  
  
Example `users.csv` file data might look like this: 

userid| department| access_level| location| title  
---|---|---|---|---  
ADMIN-*| IT| administrator| HQ| System Administrator  
dev-user-*| Engineering| developer| Remote| Software Engineer  
TEST_*| QA| tester| Lab| QA Engineer  
support-*| Support| agent| Office| Support Specialist  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         id =~ match(file="users.csv", column=userid, mode=glob, ignoreCase=true)

Uses glob pattern matching to match the userid column of the `users.csv` lookup table file against the IDs in the events. When an event ID matches a pattern in `users.csv`, all (non-pattern) columns from that first matching row are added to the event. The column names become new field names. 

Pattern matching examples based on the input data and lookup file are: 

`ADMIN-123` matches `ADMIN-*`

`dev-user-456` matches `dev-user-*`

`TEST_789` matches `TEST_*`

`support-001` matches `support-*`

  3. Event Result set.




### Summary and Results

The query is used to match event IDs against patterns in a user list, and then add the matching user details (other columns from the row in the `users.csv` file) to the events. 

Pattern-based matching with field enrichment is, for example, useful in case you want to add user context to authentication logs. 

Sample output from the incoming example data: 

@timestamp| id| action| source_ip| department| access_level| location| title  
---|---|---|---|---|---|---|---  
2024-01-15T09:00:00.000Z| ADMIN-123| login| 10.0.0.1| IT| administrator| HQ| System Administrator  
2024-01-15T09:01:00.000Z| dev-user-456| code_push| 10.0.0.2| Engineering| developer| Remote| Software Engineer  
2024-01-15T09:02:00.000Z| TEST_789| test_run| 10.0.0.3| QA| tester| Lab| QA Engineer  
2024-01-15T09:03:00.000Z| support-001| ticket_update| 10.0.0.4| Support| agent| Office| Support Specialist  
  
After matching, the output combines original event fields with matched user details. Only events with matching patterns appear in output.
