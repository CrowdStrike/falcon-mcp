# Perform a Left Join Query to Combine Two Datasets | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-define-table-left.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform a Left Join Query to Combine Two Datasets

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    defineTable(name="users_table",query={orgId=1},include=[username, name])
    | operation=createdFile
    | match(table=users_table, field=username, strict=false)
    | select([username, name])

### Introduction

In this example, the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function is used as a left join query to extract and combine information from two different datasets. 

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| name| orgId  
---|---|---  
user1| John Doe| 1  
user2| Jane Doe| 1  
user3| Bob Smith| 2  
  
and the other event set: 

username| operation  
---|---  
user1| createdFile  
user2| deletedFile  
user3| createdFile  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         defineTable(name="users_table",query={orgId=1},include=[username, name])

Generates an ad-hoc table named `users_table` that has the fields username and name and includes users where orgId field equals `1`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | operation=createdFile

Filters on the field operation for users who performed the action of creating a file by looking for the value `createdFile`. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | match(table=users_table, field=username, strict=false)

Joins with `users_table` table. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | select([username, name])

Selects the username and name fields to be displayed from the event set. 

  6. Event Result set.




### Summary and Results

The result will output two events: 

username| name  
---|---  
user1| John Doe  
user3| no value  
  
where user3 has no value since this user is not included in the `users_table` table `user2` (not belonging to orgId=1).
