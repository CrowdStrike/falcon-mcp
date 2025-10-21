# Match Hashed Values in Specific Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-hashmatch-filter-ssn.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Match Hashed Values in Specific Fields

Match events where a field equals a hashed value using the [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    ssn =~ hashMatch("456-78-9012", salt="salt1")

### Introduction

The [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function can be used to filter events by comparing a field value against a hashed string. This is particularly useful when working with sensitive data where the original values have been hashed for security purposes. 

In this example, the [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function is used to filter events where the ssn field matches the hash of a specific value, using a specified [_`salt`_](https://library.humio.com/data-analysis/functions-hashmatch.html#query-functions-hashmatch-salt) value for the hashing. A salt is a random string added to the data before hashing to make the hash more secure. 

Note that the example uses the [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function with the comparison operator `=~` to match against a specific field. 

Example incoming data might look like this: 

@timestamp| action| ssn| user_id  
---|---|---|---  
2025-09-01T10:00:00Z| profile_update| C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8| user1  
2025-09-01T10:00:05Z| new_account| C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8| user2  
2025-09-01T10:00:10Z| profile_view| naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ| user3  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ssn =~ hashMatch("456-78-9012", salt="salt1")

Filters events where the ssn field value matches the hash of `456-78-9012`. The [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function creates a hash using the specified string and [_`salt`_](https://library.humio.com/data-analysis/functions-hashmatch.html#query-functions-hashmatch-salt) value (`salt1`), then compares it against the value in the ssn field. 

The [_`salt`_](https://library.humio.com/data-analysis/functions-hashmatch.html#query-functions-hashmatch-salt) parameter is required and should match the salt used when the original data was hashed (in this case `salt1`). For more information, see [Hash Field Values Using `hashRewrite()` ](examples-hashrewrite-field-value.html "Hash Field Values Using hashRewrite\(\)"). 

  3. Event Result set.




### Summary and Results

The query is used to find events where a hashed field matches an expected value without exposing the original sensitive data. 

This query is useful, for example, to track specific user activities in logs where sensitive information like social security numbers are stored in hashed form for security compliance. 

Sample output from the incoming example data: 

@timestamp| action| ssn| user_id  
---|---|---|---  
2025-09-01T10:00:10Z| profile_view| naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ| user3  
  
Only events where the hashed value in ssn matches the hash of `456-78-9012` are included in the results. 

This example demonstrates searching for specific hashed values in a named field. For searching hashed values anywhere in event data, see [Match Events Containing Specific Hash Values](examples-hashmatch-filter.html "Match Events Containing Specific Hash Values"). To learn how to create hashed values that can be searched this way, see [Hash Field Values Using `hashRewrite()` ](examples-hashrewrite-field-value.html "Hash Field Values Using hashRewrite\(\)").
