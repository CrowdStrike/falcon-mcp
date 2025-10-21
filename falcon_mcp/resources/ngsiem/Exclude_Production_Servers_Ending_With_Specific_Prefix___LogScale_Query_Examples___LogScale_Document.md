# Exclude Production Servers Ending With Specific Prefix | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-text-endswith-exclude-prod-environment.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Exclude Production Servers Ending With Specific Prefix

Filter out servers that end with the production suffix using the [`text:endsWith()`](https://library.humio.com/data-analysis/functions-text-endswith.html) function with negation 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    !text:endsWith(string=hostname, substring="prod")

### Introduction

The [`text:endsWith()`](https://library.humio.com/data-analysis/functions-text-endswith.html) function can be negated using `!` to exclude events where a field value ends with a specified substring. 

In this example, the negated [`text:endsWith()`](https://library.humio.com/data-analysis/functions-text-endswith.html) function is used to filter out events where the hostname ends with `prod`, showing all non-production servers. 

Example incoming data might look like this: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-prod| running| us-east  
2023-06-06T10:00:01Z| db-prod| stopped| us-west  
2023-06-06T10:00:02Z| app-server-dev| running| eu-west  
2023-06-06T10:00:03Z| cache-prod| running| us-east  
2023-06-06T10:00:04Z| api-server-test| stopped| eu-west  
2023-06-06T10:00:05Z| queue-prod| running| us-west  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         !text:endsWith(string=hostname, substring="prod")

Filters events where the value in the hostname field does NOT end with `prod`. 

The exclamation mark (!) negates the function, inverting the match. The [_`string`_](https://library.humio.com/data-analysis/functions-text-endswith.html#query-functions-text-endswith-string) parameter specifies the field to check, and the [_`substring`_](https://library.humio.com/data-analysis/functions-text-endswith.html#query-functions-text-endswith-substring) parameter defines the suffix to exclude. The comparison remains case-sensitive. 

  3. Event Result set.




### Summary and Results

The query is used to filter events by excluding production servers, showing only development and test environments. 

This query is useful, for example, to monitor non-production infrastructure, analyze events from development and test environments, or focus on pre-production testing activities. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:02Z| app-server-dev| running| eu-west  
2023-06-06T10:00:04Z| api-server-test| stopped| eu-west  
  
Note that all events where hostname does NOT end with `prod` are included in the results. This effectively shows only development and test servers. The negation excludes any hostname that ends exactly with `prod`, regardless of what comes before it.
