# Perform a Nested Join Query to Combine Two Datasets and Two Tables | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-define-table-nested.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform a Nested Join Query to Combine Two Datasets and Two Tables

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3[/Filter/] 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result

logscale
    
    
    defineTable(name="organization_table",query={orgId=1},include=[username, orgId],view=organizations)
    | defineTable(name="users_table",query={match(table=organization_table, field=username)},include=[username, name])
    | operation=createdFile
    | match(table=users_table, field=username)
    | select([username, name])

### Introduction

Similar to the [inner join](examples-define-table-inner.html "Perform an Inner Join Query to Combine Two Datasets") example, [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) first creates a separate table for organizations belonging to a different view, which is then matched against a users' table as a nested-like join. 

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| orgId  
---|---  
user1| 1  
user2| 1  
user3| 2  
  
and the other event set: 

username| name  
---|---  
user1| John Doe  
user2| Jane Doe  
user3| Bob Smith  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3[/Filter/] 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         defineTable(name="organization_table",query={orgId=1},include=[username, orgId],view=organizations)

Generates an ad-hoc table named `organization_table` that has the fields username and orgId and includes users where orgId field equals `1` from the `organizations` view. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3[/Filter/] 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | defineTable(name="users_table",query={match(table=organization_table, field=username)},include=[username, name])

Generates an ad-hoc table named `users_table` that has the fields username and name and enriches rows with orgId=1 from `organization_table`

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3[/Filter/] 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | operation=createdFile

Filters on the field operation for users who performed the action of creating a file by looking for the value `createdFile`. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3[/Filter/] 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | match(table=users_table, field=username)

Joins with `users_table` table, to filter out users who are not from orgId=1 and to enrich with the users' names. 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3[/Filter/] 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | select([username, name])

Selects the username and name fields to be displayed from the event set. 

  7. Event Result set.




### Summary and Results

The result will output one event: 

username| name  
---|---  
user1| John Doe
