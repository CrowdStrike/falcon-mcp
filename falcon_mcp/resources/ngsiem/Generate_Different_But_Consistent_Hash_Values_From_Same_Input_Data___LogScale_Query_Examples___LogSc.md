# Generate Different But Consistent Hash Values From Same Input Data | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-hash-seed-parameter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Generate Different But Consistent Hash Values From Same Input Data

Generate different but consistent hash values from the same input data using the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function with seed 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] 2[(Function)] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    hash(field=user_id, limit=5, as="hash1")
    | hash(field=user_id, limit=5, seed=10, as="hash2")
    | hash(field=user_id, limit=5, seed=20, as="hash3")

### Introduction

The [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function can be used with a _`seed`_ parameter to generate different but consistent hash values from the same input data. The seed acts as an initialization value for the hash algorithm, allowing you to create different hash distributions while maintaining consistency within each seeded calculation. 

In this example, the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function is used with different _`seed`_ values to demonstrate how the same input data can generate different hash values. This is useful when you need multiple independent but consistent ways to group or sample the same data. 

Example incoming data might look like this: 

@timestamp| user_id| action| department  
---|---|---|---  
2023-06-15T10:00:00Z| user123| login| sales  
2023-06-15T10:00:01Z| user456| logout| marketing  
2023-06-15T10:00:02Z| user123| view| sales  
2023-06-15T10:00:03Z| user789| login| engineering  
2023-06-15T10:00:04Z| user456| login| marketing  
2023-06-15T10:00:05Z| user123| search| sales  
2023-06-15T10:00:06Z| user789| logout| engineering  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] 2[(Function)] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         hash(field=user_id, limit=5, as="hash1")

Creates hash values from the user_id field and returns the results in the field hash1. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] 2[(Function)] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | hash(field=user_id, limit=5, seed=10, as="hash2")

Creates a second set of hash values from the same user_id field but uses a _`seed`_ value of `10` and returns the results in the field hash2. Using a different seed value creates a different but equally consistent distribution of hash values. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] 2[(Function)] 3[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | hash(field=user_id, limit=5, seed=20, as="hash3")

Creates a third set of hash values using a _`seed`_ value of `20` and returns the results in the field hash3. This demonstrates how different seed values create different hash distributions for the same input data. 

  5. Event Result set.




### Summary and Results

The query is used to generate different but consistent hash values from the same input data by using different _`seed`_ values. 

This query is useful, for example, to create multiple independent sampling groups from the same data set, or to implement A/B/C testing where users need to be consistently assigned to different test groups. 

Sample output from the incoming example data: 

action| department| hash1| hash2| hash3| user_id  
---|---|---|---|---|---  
login| sales| 3| 0| 2| user123  
logout| marketing| 2| 2| 2| user456  
view| sales| 3| 0| 2| user123  
login| engineering| 4| 4| 1| user789  
login| marketing| 2| 2| 2| user456  
search| sales| 3| 0| 2| user123  
logout| engineering| 4| 4| 1| user789  
  
Important notes about the output: 

  * The same user_id always generates the same hash value within each hash field. 

  * Different seed values create different hash values for the same input. 

  * The hash values remain within the specified limit range (0-4) regardless of the seed value. 

  * The distribution pattern changes with different seeds while maintaining consistency for each input value.
