# Correlate AWS Federation Token Generation with Console Logins | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-correlate-aws-federation-login.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Correlate AWS Federation Token Generation with Console Logins

Correlate AWS CloudTrail events (GetFederationToken action and ConsoleLogin action) by the same user within a 60-minute window using the [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["GetFederationToken: Table"] 3["ConsoleLogin: Table"] 4[(Function)] result{{Result Set}} repo --> 1 1 --> 2 1 --> 3 2 --> 4 3 --> 4 4 --> result

logscale
    
    
    #Vendor="aws" #event.kind="event" #event.module="cloudtrail"
    | correlate(
        GetFederationToken:{event.action="GetFederationToken"},
        ConsoleLogin:{event.action="ConsoleLogin" 
        | user.name <=> GetFederationToken.user.name},
    sequence=true,within=60m)

### Introduction

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function can be used to match and combine events from multiple queries based on specified field values within a defined time window. The set of returned events will consist of a list of events, identified by their correlation query name, and containing the matching connection fields from each event. 

In this example, the [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function is used to match AWS GetFederationToken events with corresponding ConsoleLogin events for the same user within a 60-minute window, ensuring the events occur in sequence. 

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function finds relationships between the events within the `GetFederationToken` and `ConsoleLogin` queries. `sequence=true` means that events in a constellation must occur in the order that the queries are defined within the time window 

Example incoming data might look like this: 

@timestamp| #Vendor| #event.kind| #event.module| event.action| user.name| source.ip| aws.cloudtrail.event_id  
---|---|---|---|---|---|---|---  
2023-06-15T08:00:00Z| aws| event| cloudtrail| GetFederationToken| alice.smith| 10.0.1.100| a1b2c3d4  
2023-06-15T08:01:30Z| aws| event| cloudtrail| ConsoleLogin| alice.smith| 10.0.1.100| e5f6g7h8  
2023-06-15T09:15:00Z| aws| event| cloudtrail| GetFederationToken| bob.jones| 10.0.2.200| i9j0k1l2  
2023-06-15T10:25:00Z| aws| event| cloudtrail| ConsoleLogin| bob.jones| 10.0.2.200| m3n4o5p6  
2023-06-15T10:30:00Z| aws| event| cloudtrail| GetFederationToken| charlie.brown| 10.0.3.150| q7r8s9t0  
2023-06-15T11:45:00Z| aws| event| cloudtrail| ConsoleLogin| charlie.brown| 10.0.3.150| u1v2w3x4  
2023-06-15T11:00:00Z| aws| event| cloudtrail| GetFederationToken| dave.wilson| 10.0.4.175| y5z6a7b8  
2023-06-15T12:15:00Z| aws| event| cloudtrail| ConsoleLogin| dave.wilson| 10.0.4.175| c9d0e1f2  
2023-06-15T12:45:00Z| aws| event| cloudtrail| GetFederationToken| eve.parker| 10.0.5.225| g3h4i5j6  
2023-06-15T12:46:15Z| aws| event| cloudtrail| ConsoleLogin| eve.parker| 10.0.5.225| k7l8m9n0  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["GetFederationToken: Table"] 3["ConsoleLogin: Table"] 4[(Function)] result{{Result Set}} repo --> 1 1 --> 2 1 --> 3 2 --> 4 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #Vendor="aws" #event.kind="event" #event.module="cloudtrail"

Filters for events from #Vendor=`aws` with #event.kind=`event` and #event.module=`cloudtrail`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["GetFederationToken: Table"] 3["ConsoleLogin: Table"] 4[(Function)] result{{Result Set}} repo --> 1 1 --> 2 1 --> 3 2 --> 4 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | correlate(
             GetFederationToken:{event.action="GetFederationToken"},

Defines the first query named GetFederationToken to match AWS federation token generation events. Filters for events with event.action=`GetFederationToken` which captures all AWS Security Token Service (STS) federation token creation requests. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["GetFederationToken: Table"] 3["ConsoleLogin: Table"] 4[(Function)] result{{Result Set}} repo --> 1 1 --> 2 1 --> 3 2 --> 4 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ConsoleLogin:{event.action="ConsoleLogin" 
             | user.name <=> GetFederationToken.user.name},

Defines the second query named ConsoleLogin to match AWS console login attempts. Filters for events with event.action=`ConsoleLogin` which captures all AWS Management Console authentication events. 

The correlation relationship (condition) is specified using the ``<=>`` operator which requires exact matches between fields (field correlation matches). 

The user.name field from this ConsoleLogin event must match the user.name field from the GetFederationToken event. The corresponding fields will be used to join the events together across all the queries in the set. This ensures that events will only be correlated when they relate to the same user's authentication sequence, preventing false correlations between different users' token generations and logins. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2["GetFederationToken: Table"] 3["ConsoleLogin: Table"] 4[(Function)] result{{Result Set}} repo --> 1 1 --> 2 1 --> 3 2 --> 4 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sequence=true,within=60m)

Sets correlation parameters: 

     * [_`sequence`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-sequence)=`true` ensures that GetFederationToken events must occur before ConsoleLogin events. 

     * [_`within`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-within)=`60m` specifies that the console login must occur within 60 minutes of token generation, matching the typical federation token validity period. 

By default, the query will match the event correlation only once per root query (return the first match), as the [_`maxPerRoot`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-maxperroot) parameter is not specified. 

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function outputs each pair of matched events as a single event containing fields from both sources, prefixed with their respective subquery names (for example, GetFederationToken.user.name, consoleLogin.@timestamp). 

  6. Event Result set.




### Summary and Results

The query is used to track the complete authentication flow for federated users accessing the AWS Console, ensuring proper sequence and timing of authentication events. The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function tracks authentication sequences by matching federation token generation events with subsequent console login attempts within a specified time window. 

This query is useful, for example, to monitor federation token usage patterns, detect potential token sharing or misuse, and verify that console logins occur within expected timeframes after token generation. 

Sample output from the incoming example data: 

@timestamp| GetFederationToken.user.name| GetFederationToken.source.ip| GetFederationToken.aws.cloudtrail.event_id| ConsoleLogin.@timestamp| ConsoleLogin.source.ip| ConsoleLogin.aws.cloudtrail.event_id| TimeBetweenEvents  
---|---|---|---|---|---|---|---  
2023-06-15T08:00:00Z| alice.smith| 10.0.1.100| a1b2c3d4| 2023-06-15T08:01:30Z| 10.0.1.100| e5f6g7h8| 90  
2023-06-15T09:15:00Z| bob.jones| 10.0.2.200| i9j0k1l2| 2023-06-15T10:25:00Z| 10.0.2.200| m3n4o5p6| 4200  
2023-06-15T12:45:00Z| eve.parker| 10.0.5.225| g3h4i5j6| 2023-06-15T12:46:15Z| 10.0.5.225| k7l8m9n0| 75  
  
Note that the following events are excluded from the results because their ConsoleLogin occurred more than `60` minutes after the GetFederationToken: 

  * charlie.brown's login at 11:45:00Z (75 minutes after token generation at 10:30:00Z) 

  * dave.wilson's login at 12:15:00Z (75 minutes after token generation at 11:00:00Z) 




This demonstrates how the [_`within`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-within)=`60m` parameter filters out login attempts that occur outside the expected federation token usage window. 

Note that the output includes timestamps from each query. The TimeBetweenEvents field shows the seconds between token generation and console login, useful for identifying unusual login patterns.
