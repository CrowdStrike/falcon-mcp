# Exclude Servers Beginning With Specific Prefix | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-text-startswith-hostname-web-exclude.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Exclude Servers Beginning With Specific Prefix

Filter out servers that begin with a specific prefix using the [`text:startsWith()`](https://library.humio.com/data-analysis/functions-text-startswith.html) function with negation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    !text:startsWith(string=hostname, substring="web-")

### Introduction

The [`text:startsWith()`](https://library.humio.com/data-analysis/functions-text-startswith.html) function can be negated using `!` to exclude events where a field value begins with a specified substring. 

In this example, the negated [`text:startsWith()`](https://library.humio.com/data-analysis/functions-text-startswith.html) function is used to filter out events where the hostname begins with `web-`, showing all non-web servers. 

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
         
         !text:startsWith(string=hostname, substring="web-")

Filters events where the value in the hostname field does NOT start with `web-`. 

The exclamation mark (!) negates the function, inverting the match. The [_`string`_](https://library.humio.com/data-analysis/functions-text-startswith.html#query-functions-text-startswith-string) parameter specifies the field to check, and the [_`substring`_](https://library.humio.com/data-analysis/functions-text-startswith.html#query-functions-text-startswith-substring) parameter defines the prefix to exclude. The comparison remains case-sensitive. 

  3. Event Result set.




### Summary and Results

The query is used to filter events by excluding servers with specific naming conventions, showing all non-web servers. 

This query is useful, for example, to monitor all backend infrastructure excluding web servers, analyze events from supporting services, or focus on specific server types by excluding others. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:01Z| webapp-prod-02| stopped| us-west  
2023-06-06T10:00:02Z| db-server-03| running| eu-west  
2023-06-06T10:00:04Z| app-server-05| stopped| eu-west  
  
Note that all events where hostname does NOT begin with `web-` are included in the results. The negation excludes only exact matches of the prefix `web-`.
