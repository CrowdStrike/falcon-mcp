# Match Events Containing Specific Hash Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-hashmatch-filter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Match Events Containing Specific Hash Values

Match events containing a specific hashed value using the [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    hashMatch("456-78-9012", salt="salt1")

### Introduction

The [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function can be used to filter events by matching a specific value against hashed data in your events. It creates a hash of the provided value using the specified salt and matches it against the event data. A salt is a random string added to the data before hashing to make the hash more secure. 

In this example, the [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function is used to find events where the value `456-78-9012` appears in the event data as a hash created with the [_`salt`_](https://library.humio.com/data-analysis/functions-hashmatch.html#query-functions-hashmatch-salt) equal to `salt1`. 

Example incoming data might look like this: 

@timestamp| @rawstring  
---|---  
2025-09-01T10:00:00Z| User logged in with hash:C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8  
2025-09-01T10:00:05Z| Failed login attempt hash:C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8  
2025-09-01T10:00:10Z| Password reset requested hash:naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         hashMatch("456-78-9012", salt="salt1")

Filters events by checking if the hash of value `456-78-9012` (created using the salt `salt1`) appears anywhere in the [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field. The function creates the hash using the provided value and salt, then searches for this hash pattern in the event data. 

  3. Event Result set.




### Summary and Results

The query is used to filter events that contain a specific hashed value in their content. 

This query is useful, for example, to search for specific sensitive values in logs where the values have been hashed for security purposes, such as finding events related to a specific user ID or account number that has been hashed in the logs. 

Sample output from the incoming example data: 

@timestamp| @rawstring  
---|---  
2025-09-01T10:00:10Z| Password reset requested hash:naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ  
  
Note that the salt value must match the one used when the original hash was created in the data. The function searches for the hash pattern anywhere in the event data. 

This example shows how to search for hashed values anywhere in event data. For searching in specific fields, see [Match Hashed Values in Specific Fields](examples-hashmatch-filter-ssn.html "Match Hashed Values in Specific Fields"). To understand how to create searchable hashed data, see [Hash Field Values Using `hashRewrite()` ](examples-hashrewrite-field-value.html "Hash Field Values Using hashRewrite\(\)").
