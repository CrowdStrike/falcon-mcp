# Convert Timestamp Values Into Formatted Strings | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-format-epoch-timestamp-hour.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Timestamp Values Into Formatted Strings

Converting epoch timestamp to hour format using the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function with a format specifier 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    format("%tH", field=@timestamp, as=hour)
    table(hour)

### Introduction

The [`format()`](https://library.humio.com/data-analysis/functions-format.html) function can be used to format values according to specified patterns, particularly useful for formatting epoch timestamps (milliseconds since 1970) into specific date/time string representations. 

In this example, the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function is used to format the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field (containing milliseconds since epoch) to show the time in `HOUR` format using the format specifier `%tH`. 

Example incoming data might look like this: 

@timestamp| action| user| status  
---|---|---|---  
1686837825000| login| john| success  
1686839112000| logout| john| success  
1686840753000| login| alice| success  
1686842415000| download| alice| completed  
1686844522000| login| bob| failed  
1686845745000| login| bob| success  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         format("%tH", field=@timestamp, as=hour)

Extracts the hour (in 24-hour format) from the epoch timestamp in [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field using the format specifier `%tH` and returns the formatted results in a new field named hour. The parameter [_`field`_](https://library.humio.com/data-analysis/functions-format.html#query-functions-format-field) specifies the input field containing the epoch timestamp (in milliseconds), and [_`as`_](https://library.humio.com/data-analysis/functions-format.html#query-functions-format-as) defines the name of the output field. The pattern `%tH` specifically formats the hour in 24-hour format (00-23). 

Note that fields can only be used as date/time values if they are in milliseconds since the beginning of the Unix epoch, 1 January 1970 00:00:00 UTC. If the field is anything else, format outputs null. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         table(hour)

Displays the result of the hour field in a table. 

  4. Event Result set.




### Summary and Results

The query is used to convert epoch timestamps to readable hour format. 

Sample output from the incoming example data: 

hour  
---  
14  
15  
16  
  
The hours are displayed in 24-hour format (00-23).
