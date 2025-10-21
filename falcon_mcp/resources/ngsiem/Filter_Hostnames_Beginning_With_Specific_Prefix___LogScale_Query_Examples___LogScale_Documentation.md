# Filter Hostnames Beginning With Specific Prefix | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-text-startswith-hostname-match-web.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Hostnames Beginning With Specific Prefix

Match server names that begin with a specific prefix using the [`text:startsWith()`](https://library.humio.com/data-analysis/functions-text-startswith.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    text:startsWith(string=hostname, substring="web-")

### Introduction

The [`text:startsWith()`](https://library.humio.com/data-analysis/functions-text-startswith.html) function can be used to filter events by checking if a field value begins with a specified substring. It includes events when there is a match and excludes events otherwise. 

In this example, the [`text:startsWith()`](https://library.humio.com/data-analysis/functions-text-startswith.html) function is used to filter events where the hostname begins with `web-`, a common prefix for web servers. 

Example incoming data might look like this: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-01| running| us-east  
2023-06-06T10:00:01Z| webapp-prod-02| stopped| us-west  
2023-06-06T10:00:02Z| db-server-03| running| eu-west  
2023-06-06T10:00:03Z| web-prod-04| running| us-east  
2023-06-06T10:00:04Z| app-server-05| stopped| eu-west  
2023-06-06T10:00:05Z| web-test-06| running| us-west  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         text:startsWith(string=hostname, substring="web-")

Filters events where the value in the hostname field starts with `web-`. 

The [_`string`_](https://library.humio.com/data-analysis/functions-text-startswith.html#query-functions-text-startswith-string) parameter specifies the field to check, and the [_`substring`_](https://library.humio.com/data-analysis/functions-text-startswith.html#query-functions-text-startswith-substring) parameter defines the prefix to match. The function performs a case-sensitive comparison. 

  3. Event Result set.




### Summary and Results

The query is used to filter events based on server naming conventions, specifically identifying web-related servers. 

This query is useful, for example, to monitor specific server types in your infrastructure, analyze events from web servers, or filter logs based on standardized naming patterns. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-01| running| us-east  
2023-06-06T10:00:03Z| web-prod-04| running| us-east  
2023-06-06T10:00:05Z| web-test-06| running| us-west  
  
Note that only events where hostname begins with `web-` are included in the results. The match is case-sensitive, so hostnames starting with `WEB-` would not be included.
