# Find Fields With Data in Class | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-wildcard-7.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Fields With Data in Class

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    wildcard(field=class,pattern="*Data*")
    | groupBy(class)

### Introduction

Find all events containing any `Data` string in their class, and count the occurrences for each class that is found. For example, it can be used to get a list of events that have items such as DataIngestRateMonitor, or LocalDatasource. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         wildcard(field=class,pattern="*Data*")

Searches the incoming data to list all events having Data (and everything around it) in their string. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(class)

Takes the events extracted from the search and groups them by the class field. 

  4. Event Result set.




### Summary and Results

The result is an aggregated count of all events matching anything with `Data` (with one or more characters before or after), in the class field. 

class| _count  
---|---  
c.h.c.c.ChatterDataMemoryStatusLoggerJob$| 283  
c.h.d.DataIngestRateMonitor$| 7504  
c.h.d.LocalDatasource$| 10352  
c.h.d.q.EmptyIdleDatasourcesCleaner| 3  
c.h.e.e.Datasource$| 3947  
c.h.e.e.Datasources$| 4  
c.h.e.f.DataSnapshotOps$| 662  
c.h.e.f.DataWithGlobal| 7254  
c.h.j.CleanupDatasourceFilesJob| 141  
c.h.j.DataSyncJobImpl$| 46594  
c.h.j.DatasourceRehashingJob$| 32  
c.h.k.ChatterDataDistributionKafka$| 107
