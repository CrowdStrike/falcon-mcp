# Perform a Right Join Query to Combine Two Datasets | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-define-table-right.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform a Right Join Query to Combine Two Datasets

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3@{ shape: doc, label: "Source or File" } 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result

logscale
    
    
    defineTable(name="users",query={orgId=1},include=[username, name])
    | defineTable(name="operations",query={*},include=[username, operation])
    | readFile(users)
    | match(operations, field=username, strict=false)
    | select([username, operation])

### Introduction

In this example, the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function is used as a right join query to extract and combine information from two different datasets. 

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
user3| createdFile  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3@{ shape: doc, label: "Source or File" } 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         defineTable(name="users",query={orgId=1},include=[username, name])

Generates an ad-hoc table named `users` that has the fields username and name and includes users where orgId field equals `1`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3@{ shape: doc, label: "Source or File" } 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | defineTable(name="operations",query={*},include=[username, operation])

Defines a new ad-hoc table that uses all the fields (username and operation) in a table named `operations`. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3@{ shape: doc, label: "Source or File" } 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | readFile(users)

Reads the `users` ad-hoc table as events using [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html). 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3@{ shape: doc, label: "Source or File" } 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | match(operations, field=username, strict=false)

Matches the events that have a matching operation from the `operations` table with the `users` table using the username as the common field. Events are not filtered if the events do not match, (implying a right join), by using [_`strict=false`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-strict)

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: processes, label: "Multiple Tables" } 2@{ shape: win-pane, label: "Table" } 3@{ shape: doc, label: "Source or File" } 4[/Filter/] 5[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | select([username, operation])

Selects the username and operation fields to be displayed from the event set. 

  7. Event Result set.




### Summary and Results

The result will output two events: 

username| operation  
---|---  
user1| createdFile  
user2| no value  
  
Note that in the event set all operations have been included even when there is no match between the username field, resulting in the `no value` for `user2`. If [_`strict=true`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-strict) had been used to the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function, then the event for `user2` would not have been outputted.
