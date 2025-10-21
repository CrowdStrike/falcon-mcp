# List All EC2 Hosts With FirstSeen Data Within 14 Days | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-selectlast-sensor-firstseen.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## List All EC2 Hosts With FirstSeen Data Within 14 Days

List all the EC2 hosts with FirstSeen data within 14 days using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function with [`selectLast()`](https://library.humio.com/data-analysis/functions-selectlast.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"
    | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)
    | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)
    | TimeDelta := now() - duration("14d")

### Introduction

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used with [`selectLast()`](https://library.humio.com/data-analysis/functions-selectlast.html) to retrieve the latest information about `AWS EC2` instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

Example incoming data (raw data in sensor_metadata) might look like this: 

@timestamp| aid| cloud.provider| event_platform| ComputerName| AgentVersion| FirstSeen  
---|---|---|---|---|---|---  
2025-05-20T10:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15678| 2025-01-15T08:30:00Z  
2025-05-21T11:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00Z  
2025-05-22T12:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15678| 2025-02-01T14:45:00Z  
2025-05-23T13:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00Z  
2025-05-24T14:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15678| 2025-03-10T09:15:00Z  
2025-05-25T15:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00Z  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"

Searches in the sensor_metadata repository, and filters for #data_source_name fields containing the value `aidmaster`, looking for cloud.provider of the type `AWS_EC2_V2` only. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)

Groups results by the field aid (Agent ID). Then, for each unique group, selects the most recent values for the fields: event_platform, aid, ComputerName, AgentVersion, FirstSeen. 

Using the [`selectLast()`](https://library.humio.com/data-analysis/functions-selectlast.html) within the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) is what actually selects the most recent record for each group. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)

Formats the timestamp in the FirstSeen field into ISO 8601 format. The result is stored back in the FirstSeen field. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | TimeDelta := now() - duration("14d")

Calculates timestamp from 14 days ago, and returns the results into a new field named TimeDelta. The calculation is done by subtracting a 14-day duration from the current time using [`duration()`](https://library.humio.com/data-analysis/functions-duration.html). 

This new TimeDelta field that represents a timestamp from 14 days ago, can be used for filtering or comparing against the FirstSeen timestamps. 

  6. Event Result set.




### Summary and Results

The query is used to retrieve the latest information about AWS EC2 instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

The query is useful, for example, for auditing EC2 instance coverage, identifying newly added EC2 instances within the last two weeks, monitoring sensor versions or identifying aging or outdated installations. 

Sample output from the incoming example data: 

aid| event_platform| ComputerName| AgentVersion| FirstSeen| TimeDelta  
---|---|---|---|---|---  
1234abcd| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00+0000| 2025-05-12T13:06:56+0000  
5678efgh| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00+0000| 2025-05-12T13:06:56+0000  
90123ijk| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00+0000| 2025-05-12T13:06:56+0000  
  
Each aid appears only once with its most recent values. Note that TimeDelta value is based on the current date provided (Mon, 26 May 2025 13:06:56 GMT).
