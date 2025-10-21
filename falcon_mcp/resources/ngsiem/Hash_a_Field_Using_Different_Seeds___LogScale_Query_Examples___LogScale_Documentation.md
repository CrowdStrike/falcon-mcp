# Hash a Field Using Different Seeds | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-hash-field-with-seed.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Hash a Field Using Different Seeds

Generate hash values using the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function with different seeds 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | hash_seed10 := hash(field=[username], seed=10)
    | hash_seed20 := hash(field=[username], seed=20)

### Introduction

The [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function can be used to generate deterministic hash values from field contents. The [_`seed`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-seed) parameter acts as an initialization value for the hashing algorithm, allowing you to generate different but consistent hash values for the same input. 

In this example, the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function is used to demonstrate how different seed values affect the hash output while maintaining consistency for the same input values. 

Example incoming data might look like this: 

@timestamp| username| action  
---|---|---  
2025-08-27T08:51:51.312Z| alice| login  
2025-08-27T09:15:22.445Z| bob| login  
2025-08-27T10:30:15.891Z| alice| logout  
2025-08-27T11:45:33.167Z| charlie| login  
2025-08-27T12:20:44.723Z| bob| logout  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | hash_seed10 := hash(field=[username], seed=10)
         | hash_seed20 := hash(field=[username], seed=20)

Creates two new fields with different hash values for the same input: 

     * Field hash_seed10 contains hash values generated with `seed=10`

     * Field hash_seed20 contains hash values generated with `seed=20`

The [_`field`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-field) parameter specifies [username](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) as the input field in an array format. The [_`seed`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-seed) parameter initializes the hashing algorithm with different values, producing different but consistent hash patterns. 

  3. Event Result set.




### Summary and Results

The query is used to demonstrate how different seed values affect hash generation while maintaining consistency for identical inputs. 

This query is useful, for example, to create multiple different pseudonymous identifiers for the same data, compare hash distributions with different seeds, or understand how seed values affect hash generation 

Sample output from the incoming example data: 

username| action| hash_seed10| hash_seed20  
---|---|---|---  
alice| login| 7234981073614532891| 8945672301234567890  
bob| login| 4123567890123456789| 5678901234567890123  
alice| logout| 7234981073614532891| 8945672301234567890  
charlie| login| 9876543210987654321| 2345678901234567890  
bob| logout| 4123567890123456789| 5678901234567890123  
  
Note that the same username produces different hash values with different seeds (compare hash_seed10 and hash_seed20 for `alice`). Each seed consistently produces the same hash value for the same input (notice how `alice` always has the same hash value within each seed).
