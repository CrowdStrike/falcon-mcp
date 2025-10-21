# Correlate Two Scheduled Task Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-correlate-scheduled-tasks.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Correlate Two Scheduled Task Events

Correlate two scheduled task events (registration and deletion) within a 5-minute window using the `correlate` function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["ScheduledTaskRegistered: Table"] 2["ScheduledTaskDeleted: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result

logscale
    
    
    correlate(
        ScheduledTaskRegistered: {
            #repo="base_sensor" #event_simpleName=ScheduledTaskRegistered RemoteIP=* 
        | upper(field=TaskName, as=scheduledTaskName)
        } include: [*],
      ScheduledTaskDeleted: {
              #repo="base_sensor" #event_simpleName=ScheduledTaskDeleted RemoteIP=* 
              | upper(field=TaskName, as=scheduledTaskName)
              | aid <=> ScheduledTaskRegistered.aid
              | scheduledTaskName <=> ScheduledTaskRegistered.scheduledTaskName
              } include: [*],
    sequence=false, within=5m)

### Introduction

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function can be used to match and combine events from multiple queries based on specified field values within a defined time window. The set of returned events will consist of a list of events, identified by their correlation query name, and containing the matching connection fields from each event. 

In this example, the [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function is used to identify when scheduled tasks are registered and subsequently deleted by matching events based on the task identifier (aid field) and name (TaskName field) within a 5-minute window. 

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function finds relationships between the events within the `ScheduledTaskRegistered` and `ScheduledTaskDeleted` queries. `sequence=false` means that events can occur in any order within the time window 

Example incoming data might look like this: 

@timestamp| #repo| #event_simpleName| aid| TaskName| RemoteIP  
---|---|---|---|---|---  
2023-06-15T10:00:00Z| base_sensor| ScheduledTaskRegistered| aid123| backup_task| 192.168.1.100  
2023-06-15T10:02:00Z| base_sensor| ScheduledTaskDeleted| aid123| backup_task| 192.168.1.100  
2023-06-15T10:05:00Z| base_sensor| ScheduledTaskRegistered| aid456| cleanup_task| 192.168.1.101  
2023-06-15T10:07:00Z| base_sensor| ScheduledTaskDeleted| aid456| cleanup_task| 192.168.1.101  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["ScheduledTaskRegistered: Table"] 2["ScheduledTaskDeleted: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         correlate(
             ScheduledTaskRegistered: {
                 #repo="base_sensor" #event_simpleName=ScheduledTaskRegistered RemoteIP=* 
             | upper(field=TaskName, as=scheduledTaskName)
             } include: [*],

Defines the first query named ScheduledTaskRegistered to match scheduled task registrations. Filters for events from [#repo](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-tag-repo)=`base_sensor` with #event_simpleName=`ScheduledTaskRegistered` and any RemoteIP. RemoteIP=* ensures that the field exists. 

The [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) function converts the TaskName field to uppercase and returns the converted results in a new field named scheduledTaskName. 

`include: [*]` ensures that the query includes all fields from matching events. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["ScheduledTaskRegistered: Table"] 2["ScheduledTaskDeleted: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ScheduledTaskDeleted: {
                   #repo="base_sensor" #event_simpleName=ScheduledTaskDeleted RemoteIP=* 
                   | upper(field=TaskName, as=scheduledTaskName)
                   | aid <=> ScheduledTaskRegistered.aid
                   | scheduledTaskName <=> ScheduledTaskRegistered.scheduledTaskName
                   } include: [*],

Defines the second query named ScheduledTaskDeleted to match scheduled task deletions. Filters for events from [#repo](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-tag-repo)=`base_sensor` with #event_simpleName=`ScheduledTaskDeleted` and any RemoteIP. RemoteIP=* ensures that the field exists. 

The correlation relationships (conditions) are specified using the ``<=>`` operator which requires exact matches between fields (field correlation matches). 

The aid field from this ScheduledTaskDeleted event must match the aid field from the ScheduledTaskRegistered event, and similarly for the scheduledTaskName field. The corresponding fields will be used to join the events together across all the queries in the set. This ensures that events will only by dcorrelated when related to the same task instance. 

`include: [*]` ensures that the query includes all fields from matching events. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["ScheduledTaskRegistered: Table"] 2["ScheduledTaskDeleted: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sequence=false, within=5m)

Sets correlation parameters: 

     * [_`sequence`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-sequence)=`false` allows events to match regardless of order. 

Setting the [_`sequence`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-sequence) parameter to `false` in this example is useful as `deletion events` could theoretically be recorded before `registration events` due to system delays. 

     * [_`within`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-within)=`5m` specifies a 5-minute time window for matching events meaning that only events within 5 minutes of each other will be correlated. 

By default, the query will match the event correlation only once per root query (return the first match), as the [_`maxPerRoot`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-maxperroot) parameter is not specified. 

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function outputs each pair of matched events as a single event containing fields from both sources, prefixed with their respective subquery names (for example, ScheduledTaskRegistered.aid, ScheduledTaskDeleted.@timestamp). 

  5. Event Result set.




### Summary and Results

The query is used to identify and correlate scheduled task registration and deletion events for the same task within a 5-minute window. 

The output demonstrates successful correlation of scheduled task registration and deletion events, showing the complete lifecycle of tasks that were both created and deleted within the specified timeframe. 

This query is useful, for example, to monitor task lifecycle patterns, detect unusual task deletion behavior, or audit scheduled task management activities. 

Sample output from the incoming example data: 

@timestamp| ScheduledTaskRegistered.aid| ScheduledTaskRegistered.scheduledTaskName| ScheduledTaskRegistered.RemoteIP| ScheduledTaskDeleted.@timestamp| ScheduledTaskDeleted.RemoteIP  
---|---|---|---|---|---  
2023-06-15T10:00:00Z| aid123| BACKUP_TASK| 192.168.1.100| 2023-06-15T10:02:00Z| 192.168.1.100  
2023-06-15T10:05:00Z| aid456| CLEANUP_TASK| 192.168.1.101| 2023-06-15T10:07:00Z| 192.168.1.101  
  
Note that the output includes timestamps from each query. In this case, this allows for analysis of the time between task creation and removal.
