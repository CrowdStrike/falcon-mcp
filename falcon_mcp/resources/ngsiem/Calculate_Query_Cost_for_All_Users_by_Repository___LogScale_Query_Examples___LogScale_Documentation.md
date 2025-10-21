# Calculate Query Cost for All Users by Repository | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-get-query-cost-live-static.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Query Cost for All Users by Repository

Search across multiple repositories to calculate query costs for all users by repository using [`sort()`](https://library.humio.com/data-analysis/functions-sort.html) and [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) functions 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"
     | groupBy(repo, initiatingUser, totalLiveCost, totalStaticCost)
     | sort([totalLiveCost, totalStaticCost])

### Introduction

In this example, the query uses [`sort()`](https://library.humio.com/data-analysis/functions-sort.html) and [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) functions to find query costs. The query filters logs in [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `c.h.j.RunningQueriesLoggerJob`, searching for the specific value `Highest Cost query`. 

Example incoming data might look like this: 

#type| #kind| class| message| timestamp| dataspace| initiatingUser| totalLiveCost| totalStaticCost| deltaTotalCost| repo  
---|---|---|---|---|---|---|---|---|---|---  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:30:00Z| production| john.doe| 1500| 800| 2300| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:31:00Z| development| jane.smith| 2000| 1200| 3200| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:32:00Z| staging| bob.wilson| 1000| 500| 1500| infra-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:33:00Z| production| john.doe| 1800| 900| 2700| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:34:00Z| development| jane.smith| 2500| 1300| 3800| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:35:00Z| staging| alice.cooper| 1200| 600| 1800| infra-logs  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"

Filters for Humio internal logs containing `c.h.j. RunningQueriesLoggerJob` in the class field and where the value in the message field is equal to `Highest Cost query`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(repo, initiatingUser, totalLiveCost, totalStaticCost)

Groups the results by the repo field, the initiatingUser field, and by both cost types (the fields totalLiveCost, totalStaticCost), and returns a count in a field named _count. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | sort([totalLiveCost, totalStaticCost])

Sorts the results by both the totalLiveCost field and the totalStaticCost field, in descending order by default. 

  5. Event Result set.




### Summary and Results

The query is used to search across multiple repositories and output query costs for all users by repository. The query returns the count in a field named _count. Use this query to focus on live and static costs separately. 

Sample output from the incoming example data: 

repo| initiatingUser| totalLiveCost| totalStaticCost| _count  
---|---|---|---|---  
app-logs| jane.smith| 2000| 1200| 1  
security-logs| john.doe| 1500| 800| 1  
infra-logs| bob.wilson| 1000| 500| 1
