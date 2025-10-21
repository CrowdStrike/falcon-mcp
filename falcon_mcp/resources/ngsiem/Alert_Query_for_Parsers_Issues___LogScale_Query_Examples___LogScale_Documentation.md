# Alert Query for Parsers Issues | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-alert-parsers.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Alert Query for Parsers Issues

Reporting errors 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result

logscale
    
    
    #type=humio #kind=logs
    | loglevel=WARN
    | class = c.h.d.ParserLimitingJob
    | "Setting reject ingest for"
    | groupBy(id, function=[count(), min(@timestamp), max(@timestamp)] )
    | timeDiff:=_max-_min
    | timeDiff > 300000 and _count > 10

### Introduction

This alert query tries to balance reacting when there are problems with parsers, without being too restrictive. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=humio #kind=logs

Filters on all logs across all hosts in the cluster. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | loglevel=WARN

Filters for all events where the loglevel is equal to `WARN`. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | class = c.h.d.ParserLimitingJob

Assigns the value `c.h.d.ParserLimitingJob` to the class for the logs having the loglevel value `WARN`. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | "Setting reject ingest for"

Filters for events containing the string `Setting reject ingest for`. This is the error message generated when ingested events are rejected. 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(id, function=[count(), min(@timestamp), max(@timestamp)] )

Groups the returned result by the field id, makes a count on the events and returns the minimum timestamp and maximum timestamp. This returns a new event set, with the fields id, _count, _min, and _max. 

  7. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result style 6 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | timeDiff:=_max-_min

Calculates the time difference between the maximum timestamp values and the minimum timestamp values and returns the result in a new field named timeDiff. 

  8. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4[/Filter/] 5{{Aggregate}} 6["Expression"] 7["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> 7 7 --> result style 7 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | timeDiff > 300000 and _count > 10

Returns all events where the values of timeDiff is greater that `300000` and where there are more than `10` occurrences. 

  9. Event Result set.




### Summary and Results

This query is used to set up alerts for parsers issues. Setting up alerts for parsers issues will allow to proactively reach out to customers where their queries are being throttled and help them.
