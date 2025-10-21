# Show Offline Nodes | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-offline-nodes.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Show Offline Nodes

Show the list of available nodes currently in an offline state 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #type=humio #kind=logs class=/ClusterHostAliveStats/  "AliveStats on me"
    age > 7200000 /* =2hours */
    timeChart(hostId, function=count(hostId,distinct=true), limit=50, minSpan=4h)

### Introduction

"Node Offline" events within LogScale are generated when a node is reported offline by the other nodes in the cluster. This query shows Offline Nodes. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=humio #kind=logs class=/ClusterHostAliveStats/  "AliveStats on me"

Filters on all logs in [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `/ClusterHostAliveStats/`, and where the logline contains the string `AliveStats on me`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         age > 7200000 /* =2hours */

Returns all events where the values of the field age is greater than `7200000 ms`. Notice that this example uses multi-line comments `/* =2hours */` to help describe the value which we can describe in more detail by looking at each stage of the calculation as shown below: 

none
         
         7200000ms / 1000 # 7200 seconds
         / 60 # 120 minutes
         / 60 # 2 hours
         = 2

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(hostId, function=count(hostId,distinct=true), limit=50, minSpan=4h)

Counts the events grouping by the field hostId, creating an aggregate list and displaying the last 50 returned results in buckets of 4 hours in a [`Time Chart`](https://library.humio.com/data-analysis/widgets-timechart.html). 

  5. Event Result set.




### Summary and Results

The query is used to show a list of available nodes currently in an offline state.
