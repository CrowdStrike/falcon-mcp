# Calculate Query Costs by User and Repository in a Single Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-get-query-cost-combined.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Query Costs by User and Repository in a Single Field

Calculate query costs by user across multiple repositories, showing the repository/user as a single field 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3{{Aggregate}} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"
    | repoUser:= format("%s/%s", field=[dataspace, initiatingUser])
    | top(repoUser, sum=deltaTotalCost, as=cost)
    |table([cost, repoUser], sortby=cost)

### Introduction

In this example, the query filter events in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `c.h.j.RunningQueriesLoggerJob`, searching for the specific value `Highest Cost query`. The query then combines the results in a new field repoUser. The query then uses [`top()`](https://library.humio.com/data-analysis/functions-top.html) and [`table()`](https://library.humio.com/data-analysis/functions-table.html) functions to aggregate and display the results. 

Example incoming data might look like this: 

#type| #kind| class| message| timestamp| dataspace| initiatingUser| totalLiveCost| totalStaticCost| deltaTotalCost| repo  
---|---|---|---|---|---|---|---|---|---|---  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:30:00Z| production| john.doe| 1500| 800| 2300| security-logs  
humio| logs c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:31:00Z| development| jane.smith| 2000| 1200| 3200| app-logs|   
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:32:00Z| staging| bob.wilson| 1000| 500| 1500| infra-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:33:00Z| production| john.doe| 1800| 900| 2700| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:34:00Z| development| jane.smith| 2500| 1300| 3800| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:35:00Z| staging| alice.cooper| 1200| 600| 1800| infra-logs  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3{{Aggregate}} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"

Filters for Humio internal logs containing `c.h.j. RunningQueriesLoggerJob` in the class field and where the value in the message field is equal to `Highest Cost query`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3{{Aggregate}} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | repoUser:= format("%s/%s", field=[dataspace, initiatingUser])

Combines the fields dataspace and initiatingUser with a `/` separator, and then assigns the combined value to a new field named repoUser. Example of combined value: `dataspace/username`. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3{{Aggregate}} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | top(repoUser, sum=deltaTotalCost, as=cost)

Finds the most common values in the field repoUser, makes a sum of the field deltaTotalCost, and returns the results in a new field named cost. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3{{Aggregate}} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         |table([cost, repoUser], sortby=cost)

Displays the results in a table with fields `cost` and `repoUser`, sorted by the column `cost`. 

  6. Event Result set.




### Summary and Results

The query is used to search across multiple repositories and calculate query costs per user, by combining costs and showing the repository/user as a single field. 

Sample output from the incoming example data: 

cost| repoUser  
---|---  
3200| development/jane.smith  
2300| production/john.doe  
1500| staging/bob.wilson
