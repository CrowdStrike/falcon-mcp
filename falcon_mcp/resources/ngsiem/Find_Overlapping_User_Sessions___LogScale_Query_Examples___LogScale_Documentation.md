# Find Overlapping User Sessions | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-neighbor-session-overlap-within.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Overlapping User Sessions

Detect when user sessions overlap in time using the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function within [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{Conditional} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    groupBy(user.id, function=neighbor(include=[startTime, endTime], prefix=previous))
    | groupBy(user.id, function=neighbor(direction=succeeding, include=[startTime, endTime], prefix=next))
    | case {
            test(startTime <= previous.endTime) | overlaps := "previous";
            test(endTime >= next.startTime) | overlaps := "next";
            }
    | select([user.id, startTime, endTime, overlaps, previous.startTime, previous.endTime, next.startTime, next.endTime])

### Introduction

The [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function can be used to access data from preceding or succeeding events within a group, allowing comparison between current and neighboring events. When used as part of a [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function, it provides a performance benefit and ensures correctness over most other methods of achieving the same thing. 

In this example, the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function is used to identify overlapping user sessions by comparing session start and end times with both previous and next sessions for each user. The function is implemented as part of [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) operations for optimal performance, as this approach processes the data in a single pass. 

Example incoming data might look like this: 

@timestamp| user.id| startTime| endTime  
---|---|---|---  
2025-08-06T10:00:00Z| user1| 2025-08-06T10:00:00Z| 2025-08-06T10:30:00Z  
2025-08-06T10:15:00Z| user1| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z  
2025-08-06T10:45:00Z| user1| 2025-08-06T10:45:00Z| 2025-08-06T11:15:00Z  
2025-08-06T10:00:00Z| user2| 2025-08-06T10:00:00Z| 2025-08-06T10:20:00Z  
2025-08-06T10:30:00Z| user2| 2025-08-06T10:30:00Z| 2025-08-06T10:50:00Z  
2025-08-06T11:00:00Z| user2| 2025-08-06T11:00:00Z| 2025-08-06T11:20:00Z  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{Conditional} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(user.id, function=neighbor(include=[startTime, endTime], prefix=previous))

Groups events by user.id and uses [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) to access the previous session's startTime and endTime. The [_`prefix`_](https://library.humio.com/data-analysis/functions-neighbor.html#query-functions-neighbor-prefix) parameter adds `previous.` to the field names in the output. Using [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) as part of the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is significantly more efficient than using it separately, as it allows the operation to be performed during group creation, eliminating the need for additional filtering and transformation steps to manually find sessions for particular users. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{Conditional} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(user.id, function=neighbor(direction=succeeding, include=[startTime, endTime], prefix=next))

Groups events by user.id again and uses [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) to access the next session's startTime and endTime. The [_`direction`_](https://library.humio.com/data-analysis/functions-neighbor.html#query-functions-neighbor-direction) parameter is set to `succeeding` to look at the next event, and the prefix adds `next.` to the field names. This second grouping operation maintains the performance benefits of integrating [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) within [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html). 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{Conditional} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | case {
                 test(startTime <= previous.endTime) | overlaps := "previous";
                 test(endTime >= next.startTime) | overlaps := "next";
                 }

Uses a case statement to evaluate two conditions and returns the results in a new field named overlaps. The field indicates whether a session overlaps with either its previous or next session: 

     * First test: ` test(startTime <= previous.endTime) ` checks if the current session starts before or at the same time as when the previous session ends. If true, it assigns `previous` to the overlaps field. 

     * Second test: ` test(endTime >= next.startTime) ` checks if the current session ends after or at the same time as when the next session starts. If true, it assigns `next` to the overlaps field. 

Note that if a session has no overlaps, the overlaps field will not be created for that event. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} 3{Conditional} 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | select([user.id, startTime, endTime, overlaps, previous.startTime, previous.endTime, next.startTime, next.endTime])

Explicitly selects and orders the output fields for clarity. This ensures consistent output formatting and removes any additional fields that might have been created during the processing steps. 

  6. Event Result set.




### Summary and Results

The query is used to identify user sessions that overlap in time with either their previous or next sessions. 

This query is useful, for example, to detect potential security issues where a user appears to be logged in from multiple locations simultaneously, or to identify problems with session management in applications. 

### Note

Note that this query is optimized for performance by incorporating the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function within the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) operations. This approach is significantly more efficient than applying [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) separately after grouping, as it reduces the number of processed events by the [`neighbor()`](https://library.humio.com/data-analysis/functions-neighbor.html) function and leverages LogScale's internal optimizations for grouped operations. 

Sample output from the incoming example data: 

user.id| startTime| endTime| overlaps| previous.startTime| previous.endTime| next.startTime| next.endTime  
---|---|---|---|---|---|---|---  
user1| 2025-08-06T10:00:00Z| 2025-08-06T10:30:00Z| next| <no value>| <no value>| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z  
user1| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z| previous| 2025-08-06T10:00:00Z| 2025-08-06T10:30:00Z| 2025-08-06T10:45:00Z| 2025-08-06T11:15:00Z  
user1| 2025-08-06T10:45:00Z| 2025-08-06T11:15:00Z| previous| 2025-08-06T10:15:00Z| 2025-08-06T10:45:00Z| <no value>| <no value>  
  
The output demonstrates the overlap detection: sessions are marked as overlapping with either their previous session or their next session. The overlaps field contains either `previous` or `next` depending on which neighboring session overlaps with the current session. 

The results from this query would be well-suited for visualization in a time chart widget, showing the overlapping sessions across time.
