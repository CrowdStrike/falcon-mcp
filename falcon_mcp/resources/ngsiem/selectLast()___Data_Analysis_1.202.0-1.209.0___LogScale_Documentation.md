# selectLast() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-selectlast.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`selectLast()`](functions-selectlast.html "selectLast\(\)")

Specify a set of fields to select from events; for each field it will keep the field value of the most recent event with that field. This can be used to collect field values across a range of events, where each event contributes one or more fields to the output event. It is usually most useful in combination with [`groupBy()`](functions-groupby.html "groupBy\(\)"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`fields`_](functions-selectlast.html#query-functions-selectlast-fields)[a]| array of strings| required |  |  The names of the fields to keep.   
[a] The parameter name [_`fields`_](functions-selectlast.html#query-functions-selectlast-fields) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`fields`_](functions-selectlast.html#query-functions-selectlast-fields) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     selectLast(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     selectLast(fields=["value"])
> 
> These examples show basic structure only.

### [`selectLast()`](functions-selectlast.html "selectLast\(\)") Syntax Examples

Given event data like {id:a, from:x}, {id:a, to:x}, — a table with {id, from, to} tuples. 

logscale
    
    
    groupBy(id, function=selectLast([from,to]))

There is no function for a logical opposite (select the first matching event for a given field) of the [`selectLast()`](functions-selectlast.html "selectLast\(\)") function, but for an arbitrary array of values as in the previous example, the equivalent to [`selectLast([from,to])`](functions-selectlast.html "selectLast\(\)") query would be: 

logscale
    
    
    [
     { from = *
    | head(1)
    | select(from) },
     { to = *
    | head(1)
    | select(to) }
    ]

When working with the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field, the query: 
    
    
    selectLast([@timestamp])

Is equivalent to using [`max()`](functions-max.html "max\(\)"): 
    
    
    max(@timestamp)

The opposite operation can be achieved by using [`min()`](functions-min.html "min\(\)"): 
    
    
    min(@timestamp)

### [`selectLast()`](functions-selectlast.html "selectLast\(\)") Examples

Click + next to an example below to get the full details.

#### List All EC2 Hosts With FirstSeen Data Within 14 Days

**List all the EC2 hosts with FirstSeen data within 14 days using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function with [`selectLast()`](functions-selectlast.html "selectLast\(\)") **

##### Query

logscale
    
    
    #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"
    | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)
    | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)
    | TimeDelta := now() - duration("14d")

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used with [`selectLast()`](functions-selectlast.html "selectLast\(\)") to retrieve the latest information about `AWS EC2` instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

Example incoming data (raw data in sensor_metadata) might look like this: 

@timestamp| aid| cloud.provider| event_platform| ComputerName| AgentVersion| FirstSeen  
---|---|---|---|---|---|---  
2025-05-20T10:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15678| 2025-01-15T08:30:00Z  
2025-05-21T11:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00Z  
2025-05-22T12:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15678| 2025-02-01T14:45:00Z  
2025-05-23T13:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00Z  
2025-05-24T14:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15678| 2025-03-10T09:15:00Z  
2025-05-25T15:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00Z  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"

Searches in the sensor_metadata repository, and filters for #data_source_name fields containing the value `aidmaster`, looking for cloud.provider of the type `AWS_EC2_V2` only. 

  3. logscale
         
         | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)

Groups results by the field aid (Agent ID). Then, for each unique group, selects the most recent values for the fields: event_platform, aid, ComputerName, AgentVersion, FirstSeen. 

Using the [`selectLast()`](functions-selectlast.html "selectLast\(\)") within the [`groupBy()`](functions-groupby.html "groupBy\(\)") is what actually selects the most recent record for each group. 

  4. logscale
         
         | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)

Formats the timestamp in the FirstSeen field into ISO 8601 format. The result is stored back in the FirstSeen field. 

  5. logscale
         
         | TimeDelta := now() - duration("14d")

Calculates timestamp from 14 days ago, and returns the results into a new field named TimeDelta. The calculation is done by subtracting a 14-day duration from the current time using [`duration()`](functions-duration.html "duration\(\)"). 

This new TimeDelta field that represents a timestamp from 14 days ago, can be used for filtering or comparing against the FirstSeen timestamps. 

  6. Event Result set.




##### Summary and Results

The query is used to retrieve the latest information about AWS EC2 instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

The query is useful, for example, for auditing EC2 instance coverage, identifying newly added EC2 instances within the last two weeks, monitoring sensor versions or identifying aging or outdated installations. 

Sample output from the incoming example data: 

aid| event_platform| ComputerName| AgentVersion| FirstSeen| TimeDelta  
---|---|---|---|---|---  
1234abcd| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00+0000| 2025-05-12T13:06:56+0000  
5678efgh| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00+0000| 2025-05-12T13:06:56+0000  
90123ijk| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00+0000| 2025-05-12T13:06:56+0000  
  
Each aid appears only once with its most recent values. Note that TimeDelta value is based on the current date provided (Mon, 26 May 2025 13:06:56 GMT).
