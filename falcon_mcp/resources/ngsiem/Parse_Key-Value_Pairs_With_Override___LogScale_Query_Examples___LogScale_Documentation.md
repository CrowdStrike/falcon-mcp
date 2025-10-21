# Parse Key-Value Pairs With Override | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-kvparse-override-parameter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse Key-Value Pairs With Override

Extract key-value pairs from text allowing field overrides using the [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) function with [_`override`_](https://library.humio.com/data-analysis/functions-kvparse.html#query-functions-kvparse-override) parameter 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    kvParse(field=message, override=true)

### Introduction

The [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) function can be used to parse key-value pairs from text fields and create new fields from them. When used with the [_`override`_](https://library.humio.com/data-analysis/functions-kvparse.html#query-functions-kvparse-override) parameter, it allows new fields to overwrite existing fields with the same names. 

In this example, the [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) function is used with the [_`override`_](https://library.humio.com/data-analysis/functions-kvparse.html#query-functions-kvparse-override) parameter to extract key-value pairs from a message field, with the ability to override any existing fields that have matching names. 

Example incoming data might look like this: 

@timestamp| source| status| message  
---|---|---|---  
2025-08-06T10:00:00Z| webserver1| 200| user=john.doe status=active role=admin sessionID=12345  
2025-08-06T10:00:01Z| webserver2| 404| user=jane.smith status=inactive role=user sessionID=67890  
2025-08-06T10:00:02Z| webserver1| 500| user=bob.wilson status=blocked role=guest sessionID=11111  
2025-08-06T10:00:03Z| webserver3| 200| user=alice.jones status=active role=admin sessionID=22222  
2025-08-06T10:00:04Z| webserver2| 200| user=mike.brown status=pending role=user sessionID=33333  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         kvParse(field=message, override=true)

Parses key-value pairs from the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field containing key-value formatted text. 

The [_`field`_](https://library.humio.com/data-analysis/functions-kvparse.html#query-functions-kvparse-field) parameter specifies which field contains the key-value pairs to parse. The [_`override`_](https://library.humio.com/data-analysis/functions-kvparse.html#query-functions-kvparse-override) parameter set to `true` allows the parsed values to overwrite any existing fields with matching names. Without the [_`override`_](https://library.humio.com/data-analysis/functions-kvparse.html#query-functions-kvparse-override) parameter, the function would skip creating fields that already exist in the event. 

  3. Event Result set.




### Summary and Results

The query is used to extract structured fields from key-value formatted text while allowing the new values to replace existing field values. 

This query is useful, for example, to parse log messages containing key-value pairs where the extracted values should take precedence over existing fields, or when reprocessing events where field values need to be updated from the message content. 

Sample output from the incoming example data: 

@timestamp| source| message| user| status| role| sessionID  
---|---|---|---|---|---|---  
2025-08-06T10:00:00Z| webserver1| user=john.doe status=active role=admin sessionID=12345| john.doe| active| admin| 12345  
2025-08-06T10:00:01Z| webserver2| user=jane.smith status=inactive role=user sessionID=67890| jane.smith| inactive| user| 67890  
2025-08-06T10:00:02Z| webserver1| user=bob.wilson status=blocked role=guest sessionID=11111| bob.wilson| blocked| guest| 11111  
2025-08-06T10:00:03Z| webserver3| user=alice.jones status=active role=admin sessionID=22222| alice.jones| active| admin| 22222  
2025-08-06T10:00:04Z| webserver2| user=mike.brown status=pending role=user sessionID=33333| mike.brown| pending| user| 33333  
  
Note that the original [status](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html) field values are overwritten by the parsed values from the message, and new fields ([user](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-permissionassignment-userassignments.html), role, sessionID) are created from the parsed key-value pairs.
