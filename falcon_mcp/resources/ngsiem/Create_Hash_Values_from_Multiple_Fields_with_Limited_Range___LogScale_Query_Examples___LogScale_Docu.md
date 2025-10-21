# Create Hash Values from Multiple Fields with Limited Range | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-hash-fields-limit.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Hash Values from Multiple Fields with Limited Range

Generate hash values from fields with modulo limit using the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    hash([user_id, department, action], limit=10)

### Introduction

The [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function can be used to generate a non-cryptographic hash value from field contents. By default, it returns an integer in the range [0,4294967295], but this range can be reduced using the [_`limit`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-limit) parameter which applies a modulo operation to the result. 

In this example, the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function is used to generate a hash value from multiple fields, with the result limited to a smaller range of `10` using the [_`limit`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-limit) parameter. 

Example incoming data might look like this: 

@timestamp| user_id| department| action| resource  
---|---|---|---|---  
2025-08-06T10:00:00Z| user123| sales| read| document1  
2025-08-06T10:00:01Z| user456| marketing| write| document2  
2025-08-06T10:00:02Z| user789| engineering| delete| document3  
2025-08-06T10:00:03Z| user234| sales| update| document4  
2025-08-06T10:00:04Z| user567| marketing| read| document5  
2025-08-06T10:00:05Z| user890| engineering| write| document6  
2025-08-06T10:00:06Z| user345| sales| delete| document7  
2025-08-06T10:00:07Z| user678| marketing| update| document8  
2025-08-06T10:00:08Z| user901| engineering| read| document9  
2025-08-06T10:00:09Z| user432| sales| write| document10  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         hash([user_id, department, action], limit=10)

Creates a non-cryptographic hash value from the contents of fields user_id, department, and action. While the function normally returns an integer between `0` and `4294967295`, the [_`limit`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-limit) parameter set to `10` applies a modulo operation to the hash value, ensuring the result is between `0` and `9`. 

The [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function returns the result in a field named _hash by default. This is particularly useful for reducing the number of groups in subsequent groupBy operations. 

  3. Event Result set.




### Summary and Results

The query is used to generate consistent numerical hash values from multiple fields while constraining the output to a specified range using modulo. 

This query is useful, for example, to reduce the number of distinct groups in a [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) operation when dealing with high-cardinality data, accepting that collisions will occur due to the limited output range. 

Sample output from the incoming example data: 

@timestamp| user_id| department| action| resource| _hash  
---|---|---|---|---|---  
2025-08-06T10:00:00Z| user123| sales| read| document1| 7  
2025-08-06T10:00:01Z| user456| marketing| write| document2| 3  
2025-08-06T10:00:02Z| user789| engineering| delete| document3| 5  
2025-08-06T10:00:03Z| user234| sales| update| document4| 2  
2025-08-06T10:00:04Z| user567| marketing| read| document5| 8  
  
Note that without a [_`limit`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-limit) parameter, the function would return values between `0` and `4294967295`. The [_`limit`_](https://library.humio.com/data-analysis/functions-hash.html#query-functions-hash-limit) parameter uses modulo to reduce the output range, in this case to `0-9`. 

For visualizing this data, a table widget would be effective to show the original fields alongside their hash values. When using the [`hash()`](https://library.humio.com/data-analysis/functions-hash.html) function with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html), a pie chart widget could help visualize the distribution of events across the limited hash values. To monitor the effectiveness of the hash distribution within the limited range, consider using a bar chart widget to show the frequency of each hash value.
