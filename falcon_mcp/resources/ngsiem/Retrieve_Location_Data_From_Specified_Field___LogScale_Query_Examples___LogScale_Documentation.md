# Retrieve Location Data From Specified Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-iplocation-addgeolocation-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Retrieve Location Data From Specified Field

Retrieve location data from a specified field using the [`ipLocation()`](https://library.humio.com/data-analysis/functions-iplocation.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    ipLocation(field=@rawstring)

### Introduction

The [`ipLocation()`](https://library.humio.com/data-analysis/functions-iplocation.html) function can be used to add geolocation data for IPv4 or IPv6 addresses. The function adds the following fields to the events: Country, City, Longitude, and Latitude. 

LogScale includes MaxMind's GeoLite2 data. The MaxMind database updates automatically every 5 minutes when you have a valid LogScale license. 

In this example, the [`ipLocation()`](https://library.humio.com/data-analysis/functions-iplocation.html) function is used with the [_`field`_](https://library.humio.com/data-analysis/functions-iplocation.html#query-functions-iplocation-field) parameter to retrieve location data from the @rawstring field. The default prefix value in the [_`field`_](https://library.humio.com/data-analysis/functions-iplocation.html#query-functions-iplocation-field) parameter is `ip`, but with the [_`field`_](https://library.humio.com/data-analysis/functions-iplocation.html#query-functions-iplocation-field) parameter 

defined as @rawstring, then the prefix will be `@rawstring`. 

Example incoming data might look like this: 

@rawstring  
---  
165.225.194.1  
1.2.3.4  
4.3.2.1  
8.8.8.8  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ipLocation(field=@rawstring)

Retrieves location data from the @rawstring field, and adds the fields @rawstring.country, @rawstring.city, @rawstring.lon, and @rawstring.lat to the event. 

  3. Event Result set.




### Summary and Results

The query is used to retrieve location data from the @rawstring field also adding more geolocation information to the events, such as Country, City, Longitude, and Latitude. The function automatically enriches the events with standardized location data, which enables consistent geographic analysis across the logs. This is, for example, useful for detection of suspicious access patterns from unexpected locations. 

Sample output from the incoming example data: 

@rawstring| @rawstring.city| @rawstring.country| @rawstring.lat| @rawstring.lon  
---|---|---|---|---  
165.225.194.1| Copenhagen| DK| 55.674| 12.5696  
1.2.3.4| <no value>| AU| -33.494| 143.2104  
4.3.2.1| <no value>| US| 37.751| -97.822  
8.8.8.8| <no value>| US| 37.751| -97.822
