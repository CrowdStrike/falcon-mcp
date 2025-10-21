# Parse ISO8601 Timestamps | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsetimestamp-isostandard.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse ISO8601 Timestamps

Convert ISO8601 Formatted Timestamps to Unix Epoch Milliseconds using the [`parseTimestamp()`](https://library.humio.com/data-analysis/functions-parsetimestamp.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    expiryTime := "2018-09-08T17:51:04.777Z"
      | parseTimestamp(field=expiryTime,as=newts)

### Introduction

The [`parseTimestamp()`](https://library.humio.com/data-analysis/functions-parsetimestamp.html) function can be used to parse timestamp strings into Unix epoch milliseconds. When parsing ISO8601 formatted timestamps that include timezone information, the function automatically handles the conversion without requiring a specific format string. 

In this example, the [`parseTimestamp()`](https://library.humio.com/data-analysis/functions-parsetimestamp.html) function is used to convert ISO8601 formatted timestamp strings into Unix epoch milliseconds. 

Example incoming data might look like this: 

@timestamp| event_type| expiryTime| user  
---|---|---|---  
1536426664777| session| 2018-09-08T17:51:04.777Z| john.doe  
1536426664888| session| 2018-09-08T17:51:04.888+00:00| jane.smith  
1536426664999| session| 2018-09-08T19:51:04.999+02:00| bob.wilson  
1536426665000| session| 2018-09-08T12:51:04.000-05:00| alice.jones  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         expiryTime := "2018-09-08T17:51:04.777Z"

Creates a test timestamp string in ISO8601 format with `Z` timezone indicator (UTC) and assigns it to the expiryTime field. 

Note that LogScale suports up to 9 digits (`2018-09-08T17:51:04.777777777Z`). 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseTimestamp(field=expiryTime,as=newts)

Parses the timestamp string in the expiryTime field and returns the result in the same field. By default, [`parseTimestamp()`](https://library.humio.com/data-analysis/functions-parsetimestamp.html) will overwrite the value of the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field. Here, the [_`as`_](https://library.humio.com/data-analysis/functions-parsetimestamp.html#query-functions-parsetimestamp-as) has been used to store the new timestamp value as an epoch. The function automatically recognizes the ISO8601 format with timezone information ('Z' for UTC, or offset like '+00:00'). The parsed result is stored as Unix epoch milliseconds. 

### Note

The LogScale search interface by default will format the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field as a human-readable date, even if the underlying data is an epoch in seconds. Be aware that this can hide the conversion of values when viewed within the UI as the conversion and formatting happens automatically. You can change this view in the UI using the `Format Panel`. 

  4. Event Result set.




### Summary and Results

The query is used to convert ISO8601 formatted timestamp strings into Unix epoch milliseconds, which is LogScale's native timestamp format. LogScale supports up to 9 digits (nanoseconds) and not just only 3 second-fractions. 

This query is useful, for example, to normalize timestamp fields in your data for consistent time-based analysis and correlation across different data sources. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| event_type| expiryTime| user  
---|---|---|---|---|---  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| john.doe  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| jane.smith  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| bob.wilson  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| alice.jones  
  
For further timestamp manipulation, you might want to explore the [`formatTime()`](https://library.humio.com/data-analysis/functions-formattime.html) function to format the Unix timestamp into different string representations.
