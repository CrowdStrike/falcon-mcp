# Correlate Authentication and Database Errors | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-correlate-auth-db-errors.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Correlate Authentication and Database Errors

Correlate authentication errors with subsequent database errors within a 1-hour window using the `correlate` function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["AuthError: Table"] 2["DatabaseError: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result

logscale
    
    
    correlate(
            AuthError: { 
            #event_type="authentication_error" 
            } include: [username, error_code, service],
        DatabaseError: { 
            #event_type="database_error" 
            | username <=> AuthError.username
            } include: [query_type, table_name, error_message],
    within=1h,globalConstraints=[username])

### Introduction

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function can be used to match and combine events from multiple queries based on specified field values within a defined time window. The set of returned events will consist of a list of events, identified by their correlation query name, and containing the matching connection fields from each event. 

In this example, the [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function is used to identify when authentication errors are followed by database errors by matching events based on the username ([username](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) field) within a 1-hour window. 

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function finds relationships between the events within the `AuthError` and `DatabaseError` queries. It helps identify patterns and potential causality between events sharing common attributes. 

Example incoming data might look like this: 

@timestamp| #event_type| username| error_code| service| query_type| table_name| error_message  
---|---|---|---|---|---|---|---  
2023-06-15T10:00:00Z| authentication_error| john.doe| AUTH001| login_service| <no value>| <no value>| <no value>  
2023-06-15T10:15:00Z| database_error| john.doe| <no value>| <no value>| SELECT| users| Table access denied  
2023-06-15T10:30:00Z| authentication_error| jane.smith| AUTH002| admin_portal| <no value>| <no value>| <no value>  
2023-06-15T10:45:00Z| database_error| jane.smith| <no value>| <no value>| UPDATE| accounts| Insufficient privileges  
2023-06-15T11:00:00Z| authentication_error| bob.wilson| AUTH001| login_service| <no value>| <no value>| <no value>  
2023-06-15T11:30:00Z| database_error| alice.jones| <no value>| <no value>| DELETE| logs| Operation not permitted  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["AuthError: Table"] 2["DatabaseError: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         correlate(
                 AuthError: { 
                 #event_type="authentication_error" 
                 } include: [username, error_code, service],

Defines the first query named AuthError to match authentication error events. Filters for events with #event_type=`authentication_error`. 

`include: [username, error_code, service]` specifies which fields to include from matching authentication error events. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["AuthError: Table"] 2["DatabaseError: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         DatabaseError: { 
                 #event_type="database_error" 
                 | username <=> AuthError.username
                 } include: [query_type, table_name, error_message],

Defines the second query named DatabaseError to match database error events. Filters for events with #event_type=`database_error`. 

The correlation relationship is specified using the ``<=>`` operator which requires an exact match between the [username](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) fields from both queries. 

`include: [query_type, table_name, error_message]` specifies which fields to include from matching database error events. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["AuthError: Table"] 2["DatabaseError: Table"] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 3 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         within=1h,globalConstraints=[username])

Sets correlation parameters: 

     * [_`within`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-within)=`1h` specifies a 1-hour time window for matching events meaning that only events within 1 hour of each other will be correlated. 

     * [_`globalConstraints`_](https://library.humio.com/data-analysis/functions-correlate.html#query-functions-correlate-globalconstraints)=`[username]` ensures that correlated events share the same username value. 

The [`correlate()`](https://library.humio.com/data-analysis/functions-correlate.html) function outputs each pair of matched events as a single event containing fields from both sources, prefixed with their respective subquery names (for example, AuthError.username, DatabaseError.error_message). 

  5. Event Result set.




### Summary and Results

The query is used to identify and correlate authentication errors with subsequent database errors for the same user within a 1-hour window. It identifies potential security incidents where authentication errors are followed by database errors for the same user, which could indicate attempted unauthorized access. 

The output demonstrates successful correlation of related security events, helping to identify potential security incidents where authentication issues are followed by database access problems. 

This query is useful, for example, to detect potential security breaches, investigate access control issues, or audit user activity patterns. 

Sample output from the incoming example data: 

@timestamp| AuthError.username| AuthError.error_code| AuthError.service| DatabaseError.@timestamp| DatabaseError.query_type| DatabaseError.table_name| DatabaseError.error_message  
---|---|---|---|---|---|---|---  
2023-06-15T10:00:00Z| john.doe| AUTH001| login_service| 2023-06-15T10:15:00Z| SELECT| users| Table access denied  
2023-06-15T10:30:00Z| jane.smith| AUTH002| admin_portal| 2023-06-15T10:45:00Z| UPDATE| accounts| Insufficient privileges  
  
Note that the output includes timestamps from each query, allowing analysis of the time between authentication errors and subsequent database errors. Events without matching pairs within the time window are excluded.
