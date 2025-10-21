# Filter Servers Ending With Specific suffix | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-text-endswith-prod-environment.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Servers Ending With Specific suffix

Match server names that end with a specific environment suffix using the [`text:endsWith()`](https://library.humio.com/data-analysis/functions-text-endswith.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    text:endsWith(string=hostname, substring="prod")

### Introduction

The [`text:endsWith()`](https://library.humio.com/data-analysis/functions-text-endswith.html) function can be used to filter events by checking if a field value ends with a specified substring. It includes events when there is a match and excludes events otherwise. 

In this example, the [`text:endsWith()`](https://library.humio.com/data-analysis/functions-text-endswith.html) function is used to filter events where the hostname ends with `prod`, identifying production servers. 

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
         
         text:endsWith(string=hostname, substring="prod")

Filters events where the value in the hostname field ends with `prod`. 

The [_`string`_](https://library.humio.com/data-analysis/functions-text-endswith.html#query-functions-text-endswith-string) parameter specifies the field to check, and the [_`substring`_](https://library.humio.com/data-analysis/functions-text-endswith.html#query-functions-text-endswith-substring) parameter defines the suffix to match. The function performs a case-sensitive comparison. 

  3. Event Result set.




### Summary and Results

The query is used to filter events based on server environment suffixes, specifically identifying production servers. 

This query is useful, for example, to monitor production infrastructure, analyze events from production environments, or filter logs based on server environment types. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-prod| running| us-east  
2023-06-06T10:00:01Z| db-prod| stopped| us-west  
2023-06-06T10:00:03Z| cache-prod| running| us-east  
2023-06-06T10:00:05Z| queue-prod| running| us-west  
  
Note that only events where hostname ends with `prod` are included in the results. The match is case-sensitive, so hostnames ending with `PROD` would not be included. This pattern matches common server naming conventions where the environment is indicated as a suffix.
