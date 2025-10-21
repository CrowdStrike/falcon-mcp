# S3 Archiving Backlog | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-storage-s3-archive.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## S3 Archiving Backlog

Determine the backlog for an S3 Archiving job to identify tasks affecting merges and potential disk overflow 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    #kind=logs #vhost=* /S3Archiving/i "Backlog for dataspace"
    timeChart(#vhost, function=max(count))

### Introduction

Falcon LogScale supports S3 archiving set up per repository. This query shows a continuously increasing backlog for the S3 Archiving job. Since an S3 archiving job can postpone merges, archiving ingested logs can result in disk overflow. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #kind=logs #vhost=* /S3Archiving/i "Backlog for dataspace"

Filters on all the logs that contain the vhost field. This way you can identify the different tasks. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(#vhost, function=max(count))

Formats the result in a timechart containing the field #vhost with the values of the maximum accounted jobs/tasks that have been archived. 

  4. Event Result set.




### Summary and Results

The query is used to determine the backlog for an S3 Archiving job in order to identify tasks affecting merges and potential disk overflow.
