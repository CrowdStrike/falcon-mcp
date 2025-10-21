# Parse Timestamp Without Timezone Information | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsetimestamp-timezone.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse Timestamp Without Timezone Information

Convert local time strings to timestamps with timezone specification using the [`parseTimestamp()`](https://library.humio.com/data-analysis/functions-parsetimestamp.html) function with [_`timezone`_](https://library.humio.com/data-analysis/functions-parsetimestamp.html#query-functions-parsetimestamp-timezone)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    parseTimestamp("yyyy-MM-dd'T'HH:mm:ss", field=event_time, timezone="America/New_York")

### Introduction

The [`parseTimestamp()`](https://library.humio.com/data-analysis/functions-parsetimestamp.html) function can be used to parse timestamp strings into LogScale timestamp format. When parsing timestamps that do not include timezone information, you must specify the [_`timezone`_](https://library.humio.com/data-analysis/functions-parsetimestamp.html#query-functions-parsetimestamp-timezone) parameter to ensure correct time interpretation. 

In this example, the [`parseTimestamp()`](https://library.humio.com/data-analysis/functions-parsetimestamp.html) is used to convert timestamp strings without timezone information into properly formatted timestamps by explicitly specifying the [_`timezone`_](https://library.humio.com/data-analysis/functions-parsetimestamp.html#query-functions-parsetimestamp-timezone). 

Example incoming data might look like this: 

event_time| action| user  
---|---|---  
2023-05-02T10:30:00| login| jsmith  
2023-05-02T10:35:00| logout| jsmith  
2023-05-02T10:40:00| login| awhite  
2023-05-02T10:45:00| update| awhite  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         parseTimestamp("yyyy-MM-dd'T'HH:mm:ss", field=event_time, timezone="America/New_York")

Parses the timestamp string in event_time using the specified format pattern. The [_`timezone`_](https://library.humio.com/data-analysis/functions-parsetimestamp.html#query-functions-parsetimestamp-timezone) parameter is set to `America/New_York` to properly interpret the local time. The result is stored in a new field named [@timezone](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timezone). 

Note that if the timestamp string does not contain a timezone, then one must be specified using the [_`timezone`_](https://library.humio.com/data-analysis/functions-parsetimestamp.html#query-functions-parsetimestamp-timezone) parameter, otherwise an error is generated. 

  3. Event Result set.




### Summary and Results

The query is used to convert local timestamp strings into properly formatted timestamps with timezone information. 

This query is useful, for example, to standardize timestamp fields in logs that contain local time information without explicit timezone data. 

Sample output from the incoming example data: 

@timezone| action| event_time| user  
---|---|---|---  
America/New_York| login| 2023-05-02T10:30:00| jsmith  
America/New_York| logout| 2023-05-02T10:35:00| jsmith  
America/New_York| login| 2023-05-02T10:40:00| awhite  
America/New_York| update| 2023-05-02T10:45:00| awhite
