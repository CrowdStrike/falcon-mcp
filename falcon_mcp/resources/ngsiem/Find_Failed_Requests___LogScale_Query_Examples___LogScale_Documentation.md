# Find Failed Requests | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-ingest-failed-requests.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Failed Requests

Display ingest requests that have failed due to throttling 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    #type=humio
    #kind=logs
    statuscode=503
    /msg=(?<msg>Ingest parsing exceeded the acceptable amount of time[^\.]+)\. exception/

### Introduction

API throttling is the process of limiting the number of API requests that a user can make in a certain period. A throttling error indicates that you have exceeded the limit for your account. When searching Falcon LogScale logs in the humio repository, the tag `#type`, `#kind` and `#vhost` can be used. All the logs will have `#type=humio`, a `#kind` tag, and a `#vhost` tag. This query finds individual ingest requests that fail due to being throttled. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=humio
         #kind=logs
         statuscode=503
         /msg=(?<msg>Ingest parsing exceeded the acceptable amount of time[^\.]+)\. exception/

Filters on all events from all hosts of all kinds, and filters on all logsstatus codes where the value in logstatuscode exceeds `503/msg` and returns an exception/error. The value `503/msg` is defined as the acceptable amount of time for parsing and ingest request (in this example). 

  3. Event Result set.




### Summary and Results

This query is used to find individual ingest requests that fail due to being throttled. From the returned results, you can decide whether to change the throttling period for the relevant alert or not. The best way to handle throttling is to reduce the number of concurrent requests. Be aware, that throttling is used to maintain the optimal performance and reliability of the system, as throttling limits the number of API calls or operations within a time window to prevent the overuse of resources.
