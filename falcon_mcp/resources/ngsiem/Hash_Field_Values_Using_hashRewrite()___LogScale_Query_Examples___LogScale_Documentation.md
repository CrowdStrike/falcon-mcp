# Hash Field Values Using hashRewrite()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-hashrewrite-field-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Hash Field Values Using [`hashRewrite()`](https://library.humio.com/data-analysis/functions-hashrewrite.html)

Hash sensitive data using the [`hashRewrite()`](https://library.humio.com/data-analysis/functions-hashrewrite.html) function with a [_`salt`_](https://library.humio.com/data-analysis/functions-hashrewrite.html#query-functions-hashrewrite-salt) value 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    hashRewrite(ssn, salt="salt1")

### Introduction

The [`hashRewrite()`](https://library.humio.com/data-analysis/functions-hashrewrite.html) function can be used to hash values in a specified field using a salt value. A salt is a random string added to the data before hashing to make the hash more secure. Without a salt, identical values would create identical hashes, making them vulnerable to dictionary attacks. Adding a salt ensures that even identical values produce different hashes when using different salts. 

In this example, the [`hashRewrite()`](https://library.humio.com/data-analysis/functions-hashrewrite.html) function is used to hash Social Security Numbers (SSNs) using a specified salt value ([_`salt`_](https://library.humio.com/data-analysis/functions-hashmatch.html#query-functions-hashmatch-salt) equal to `salt1`). 

Example incoming data might look like this: 

@timestamp| user_id| ssn| action  
---|---|---|---  
2025-09-01T10:00:00Z| user1| 123-45-6789| profile_update  
2025-09-01T10:00:05Z| user2| 123-45-6789| new_account  
2025-09-01T10:00:10Z| user3| 456-78-9012| profile_view  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         hashRewrite(ssn, salt="salt1")

Hashes the values in the ssn field through a multi-step process. First the [`hashRewrite()`](https://library.humio.com/data-analysis/functions-hashrewrite.html) function takes each value in the ssn field and adds the [_`salt`_](https://library.humio.com/data-analysis/functions-hashrewrite.html#query-functions-hashrewrite-salt) value `salt1` to it before hashing. The function then creates a hash of the combined value (original + salt) and replaces the original value with the resulting hash. 

Note that the salt value requires specific handling for security purposes. It must be kept consistent when searching for these values later, stored securely outside the log data, and should be different for different types of sensitive data. 

  3. Event Result set.




### Summary and Results

The query is used to securely hash sensitive SSN values while maintaining the ability to search for specific SSNs later using the same salt. 

The salt makes the hashing process more secure by: 

  * Making the hash unique even if SSNs are identical. 

  * Preventing the use of pre-computed hash tables (rainbow tables) to reverse the hash. 

  * Adding an extra layer of security beyond the basic hash. 




This query is useful, for example, when you need to protect sensitive data while still being able to analyze it. 

Sample output from the incoming example data: 

@timestamp| action| ssn| user_id  
---|---|---|---  
2025-09-01T10:00:00Z| profile_update| C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8| user1  
2025-09-01T10:00:05Z| new_account| C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8| user2  
2025-09-01T10:00:10Z| profile_view| naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ| user3  
  
Notice that identical SSNs (first two rows) produce identical hashes because they use the same salt. If you used a different salt, then the same SSNs would produce different hashes. 

The example demonstrates how to use [`hashRewrite()`](https://library.humio.com/data-analysis/functions-hashrewrite.html) in LogScale to protect sensitive data while maintaining searchability. To search for specific SSNs in the hashed data, use [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) with the same salt value. 

After hashing sensitive data using this method, you can search for specific values using the [`hashMatch()`](https://library.humio.com/data-analysis/functions-hashmatch.html) function.
