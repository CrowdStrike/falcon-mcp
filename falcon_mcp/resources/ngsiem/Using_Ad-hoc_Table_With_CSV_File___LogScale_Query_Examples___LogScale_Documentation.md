# Using Ad-hoc Table With CSV File | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-define-table-csv.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Using Ad-hoc Table With CSV File

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: win-pane, label: "Table" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    defineTable(name="users_table",query={match(file=organizations.csv, field=username)
    | orgId=1 },include=[username, name])
    | operation=createdFile
    | match(table=users_table, field=username)
    | select([username, name])

### Introduction

In this example, the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) is used to extract and combine information from two different datasets, with the mapping between username and orgId stored in a CSV file. The example file `organizations.csv` has the following content: 

CSV
    
    
    username,orgId
    user1,1
    user2,1
    user3,2

The event set for the query is in one repository, but the event set for each query is shown separately to identify the two sets of information. The first event set is: 

username| name  
---|---  
user1| John Doe  
user2| Jane Doe  
user3| Bob Smith  
  
and the other event set: 

username| operation  
---|---  
user1| createdFile  
user2| deletedFile  
user3| createdFile  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: win-pane, label: "Table" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         defineTable(name="users_table",query={match(file=organizations.csv, field=username)
         | orgId=1 },include=[username, name])

Generates an ad-hoc table named `users_table` that has the fields username and name and includes users where orgId field equals `1`. Then uses [`match()`](https://library.humio.com/data-analysis/functions-match.html) to enrich rows with orgId from `organizations.csv` file. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: win-pane, label: "Table" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | operation=createdFile

Filters on the field operation for users who performed the action of creating a file by looking for the value `createdFile`. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: win-pane, label: "Table" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | match(table=users_table, field=username)

Joins the username field with the `users_table` table, to filter out users who are not from orgId=1 and to enrich with the users' names. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: win-pane, label: "Table" } 2[/Filter/] 3[/Filter/] 4[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | select([username, name])

Selects the username and name fields to be displayed from the event set. 

  6. Event Result set.




### Summary and Results

The result will output one event: 

username| name  
---|---  
user1| John Doe
