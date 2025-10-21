# Display User Account Deletion Events in Table Format | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-table-user-accounts-deletion.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Display User Account Deletion Events in Table Format

Create a table showing deleted user accounts using the [`table()`](https://library.humio.com/data-analysis/functions-table.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #event_simpleName=UserAccountDeleted
    aid=?aid
    table([aid, UserName, UserId], limit=1000)

### Introduction

The [`table()`](https://library.humio.com/data-analysis/functions-table.html) function can be used to display query results in a tabular format, making it easier to view and analyze specific fields of interest. 

In this example, the [`table()`](https://library.humio.com/data-analysis/functions-table.html) function is used to create a structured view of deleted user accounts, displaying the account ID, [username](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html), and user ID. 

Example incoming data might look like this: 

@timestamp| event_simpleName| aid| UserName| UserId  
---|---|---|---|---  
2025-10-06 08:00:00| UserAccountDeleted| abc123| john.doe| UID001  
2025-10-06 08:15:30| UserAccountDeleted| def456| jane.smith| UID002  
2025-10-06 09:20:45| UserAccountDeleted| ghi789| bob.wilson| UID003  
2025-10-06 10:05:15| UserAccountDeleted| jkl012| sarah.jones| UID004  
2025-10-06 11:30:00| UserAccountDeleted| mno345| mike.brown| UID005  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #event_simpleName=UserAccountDeleted

Filters events where event_simpleName equals `UserAccountDeleted`

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         aid=?aid

Filters results based on a specific account ID using the parameter aid. 

`aid=` is the parameter name and `?aid` is a placeholder for the actual aid value. The question mark (`?`) indicates a parameter placeholder that will be replaced with an actual value during execution. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         table([aid, UserName, UserId], limit=1000)

Creates a table displaying the fields aid, [UserName](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html), and UserId. The [`table()`](https://library.humio.com/data-analysis/functions-table.html) function includes a [_`limit`_](https://library.humio.com/data-analysis/functions-table.html#query-functions-table-limit) parameter set to `1000` rows to prevent excessive output. 

  5. Event Result set.




### Summary and Results

The query is used to create a structured table view of user account deletion events, showing essential account information. 

This query is useful, for example, to monitor user account deletions, audit user management activities, or investigate security incidents related to account removals. 

Sample output from the incoming example data: 

aid| UserName| UserId  
---|---|---  
abc123| john.doe| UID001  
def456| jane.smith| UID002  
ghi789| bob.wilson| UID003  
jkl012| sarah.jones| UID004  
mno345| mike.brown| UID005
