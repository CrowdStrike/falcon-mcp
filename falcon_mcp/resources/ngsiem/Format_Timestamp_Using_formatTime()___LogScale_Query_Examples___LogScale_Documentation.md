# Format Timestamp Using formatTime() | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-formattime-format-timestamp-special-string.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format Timestamp Using formatTime()

Format a timestamp into a specific string pattern using the [`formatTime()`](https://library.humio.com/data-analysis/functions-formattime.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | time := formatTime("%Y/%m/%d %H:%M:%S", field=@timestamp, locale=en_US, timezone=Z)

### Introduction

The [`formatTime()`](https://library.humio.com/data-analysis/functions-formattime.html) function can be used to convert timestamp values into formatted strings using specified patterns. It supports various date and time format patterns, locales, and timezones to create customized datetime representations. 

In this example, the [`formatTime()`](https://library.humio.com/data-analysis/functions-formattime.html) function is used to format the [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field into a specific pattern with the format YYYY/MM/DD HH:mm:ss using US locale and UTC timezone and assigning the formatted timestamp to a new [time](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) field. 

Example incoming data might look like this: 

@timestamp| event_type| status  
---|---|---  
2025-08-27T08:51:51.312Z| login| success  
2025-08-27T09:15:22.445Z| logout| success  
2025-08-27T10:30:15.891Z| login| failed  
2025-08-27T11:45:33.167Z| update| success  
2025-08-27T12:20:44.723Z| login| success  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | time := formatTime("%Y/%m/%d %H:%M:%S", field=@timestamp, locale=en_US, timezone=Z)

Creates a new field named [time](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) containing the formatted timestamp. The function takes the following parameters: 

     * Format pattern `%Y/%m/%d %H:%M:%S` specifies year, month, day with forward slashes and hours, minutes, seconds with colons. 

     * [_`field`_](https://library.humio.com/data-analysis/functions-formattime.html#query-functions-formattime-field) parameter specifies the input timestamp field [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp). 

     * [_`locale`_](https://library.humio.com/data-analysis/functions-formattime.html#query-functions-formattime-locale) parameter is set to `en_US` for US-style formatting. 

     * [_`timezone`_](https://library.humio.com/data-analysis/functions-formattime.html#query-functions-formattime-timezone) parameter is set to `Z` for UTC timezone. 

  3. Event Result set.




### Summary and Results

The query is used to transform ISO 8601 timestamps into a more readable format while maintaining UTC timezone. 

This query is useful, for example, to standardize timestamp formats for reporting, create human-readable date representations in logs, or prepare data for export to systems requiring specific date formats. 

Sample output from the incoming example data: 

@timestamp| event_type| status| time  
---|---|---|---  
2025-08-27T08:51:51.312Z| login| success| 2025/08/27 08:51:51  
2025-08-27T09:15:22.445Z| logout| success| 2025/08/27 09:15:22  
2025-08-27T10:30:15.891Z| login| failed| 2025/08/27 10:30:15  
2025-08-27T11:45:33.167Z| update| success| 2025/08/27 11:45:33  
2025-08-27T12:20:44.723Z| login| success| 2025/08/27 12:20:44
