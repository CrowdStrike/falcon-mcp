# hash() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-hash.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`hash()`](functions-hash.html "hash\(\)")

Computes a non-cryptographic hash of a list of fields. The hash is returned as an integer in the range [0,4294967295]. Calling this function with the same values and the same seed (or no seed) will result in the same hash being computed. This hash is not cryptographic and should not be used to securely obscure data (instead use [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") and [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") for that). This function can, for example, be used to reduce the number of groups in a [`groupBy()`](functions-groupby.html "groupBy\(\)"), at the cost of having collisions. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-hash.html#query-functions-hash-as)|  string| optional[a] | `_hash`|  The output name of the field to set.   
[_`field`_](functions-hash.html#query-functions-hash-field)[b]| array of strings| required |  |  The fields for which to compute hash values.   
[_`limit`_](functions-hash.html#query-functions-hash-limit)|  number| optional[[a]](functions-hash.html#ftn.table-functions-hash-optparamfn) |  |  An upper bound on the number returned by this function. The returned hash will be modulo this value and thus be constrained to the range [0,limit].   
|  | **Minimum**| `1`|   
[ _`seed`_](functions-hash.html#query-functions-hash-seed)|  string| optional[[a]](functions-hash.html#ftn.table-functions-hash-optparamfn) |  |  An optional seed for the hash function.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-hash.html#query-functions-hash-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-hash.html#query-functions-hash-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     hash(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     hash(field=["value"])
> 
> These examples show basic structure only.

### [`hash()`](functions-hash.html "hash\(\)")Syntax Examples

Hash the field `a` and put the result into _hash: 

logscale
    
    
    hash(a)

Hash the fields `a`, `b`, and `c` and put the result modulo 10 into _hash

logscale
    
    
    hash([a,b,c], limit=10)

Hash the field `a` (by setting field explicitly) using a seed of 10 

logscale
    
    
    hash(field=[a], seed=10)

Group events into 10 buckets such that all events with the same value of `a` ends in the same bucket. 

logscale
    
    
    hash(a, limit=10)
    | groupBy(_hash)

### [`hash()`](functions-hash.html "hash\(\)") Examples

Click + next to an example below to get the full details.

#### Create Hash Values from Multiple Fields with Limited Range

**Generate hash values from fields with modulo limit using the[`hash()`](functions-hash.html "hash\(\)") function **

##### Query

logscale
    
    
    hash([user_id, department, action], limit=10)

##### Introduction

In this example, the [`hash()`](functions-hash.html "hash\(\)") function is used to generate a hash value from multiple fields, with the result limited to a smaller range of `10` using the [_`limit`_](functions-hash.html#query-functions-hash-limit) parameter. 

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
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         hash([user_id, department, action], limit=10)

Creates a non-cryptographic hash value from the contents of fields user_id, department, and [action](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity.html#table_logscale-repo-schema-humio-activity). While the function normally returns an integer between `0` and `4294967295`, the [_`limit`_](functions-hash.html#query-functions-hash-limit) parameter set to `10` applies a modulo operation to the hash value, ensuring the result is between `0` and `9`. 

The [`hash()`](functions-hash.html "hash\(\)") function returns the result in a field named _hash by default. This is particularly useful for reducing the number of groups in subsequent groupBy operations. 

  3. Event Result set.




##### Summary and Results

The query is used to generate consistent numerical hash values from multiple fields while constraining the output to a specified range using modulo. 

This query is useful, for example, to reduce the number of distinct groups in a [`groupBy()`](functions-groupby.html "groupBy\(\)") operation when dealing with high-cardinality data, accepting that collisions will occur due to the limited output range. 

Sample output from the incoming example data: 

@timestamp| user_id| department| action| resource| _hash  
---|---|---|---|---|---  
2025-08-06T10:00:00Z| user123| sales| read| document1| 7  
2025-08-06T10:00:01Z| user456| marketing| write| document2| 3  
2025-08-06T10:00:02Z| user789| engineering| delete| document3| 5  
2025-08-06T10:00:03Z| user234| sales| update| document4| 2  
2025-08-06T10:00:04Z| user567| marketing| read| document5| 8  
  
Note that without a [_`limit`_](functions-hash.html#query-functions-hash-limit) parameter, the function would return values between `0` and `4294967295`. The [_`limit`_](functions-hash.html#query-functions-hash-limit) parameter uses modulo to reduce the output range, in this case to `0-9`. 

For visualizing this data, a table widget would be effective to show the original fields alongside their hash values. When using the [`hash()`](functions-hash.html "hash\(\)") function with [`groupBy()`](functions-groupby.html "groupBy\(\)"), a pie chart widget could help visualize the distribution of events across the limited hash values. To monitor the effectiveness of the hash distribution within the limited range, consider using a bar chart widget to show the frequency of each hash value. 

#### Create Sample Groups Using Hash

**Create consistent sample groups of events using the[`hash()`](functions-hash.html "hash\(\)") function **

##### Query

logscale
    
    
    hash(ip_address, limit=10)
    groupBy(_hash, function=count())

##### Introduction

In this example, the [`hash()`](functions-hash.html "hash\(\)") function is used to create sample groups from web server access logs based on IP addresses. This allows for consistent grouping of events from the same IP address while limiting the total number of groups. 

Example incoming data might look like this: 

bytes_sent| ip_address| request_path| status_code| @timestamp  
---|---|---|---|---  
1532| 192.168.1.100| /home| 200| 2023-06-15T10:00:00Z  
892| 192.168.1.201| /notfound| 404| 2023-06-15T10:00:01Z  
2341| 192.168.10.100| /about| 200| 2023-06-15T10:00:02Z  
721| 192.168.15.102| /error| 500| 2023-06-15T10:00:03Z  
1267| 192.168.1.101| /contact| 200| 2023-06-15T10:00:04Z  
1843| 192.168.1.103| /products| 200| 2023-06-15T10:00:05Z  
1654| 192.168.15.100| /cart| 200| 2023-06-15T10:00:06Z  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         hash(ip_address, limit=10)

Creates a hash value from the ip_address field and returns the result in a new field named _hash (default). This creates a consistent mapping where the same IP address will always generate the same hash value. 

. 

The [_`limit`_](functions-hash.html#query-functions-hash-limit) parameter is set to `10`, which ensures the hash values are distributed across 10 buckets (0-9). All events with the same value of ip-address ends in the same bucket. 

  3. logscale
         
         groupBy(_hash, function=count())

Groups the events by the _hash field. For each group, it counts the number of events and returns the result in a new field named _count. This aggregation reduces the data to show how many events fall into each hash bucket. 

  4. Event Result set.




##### Summary and Results

The query is used to create consistent sample groups from large datasets by hashing a field value into a limited number of buckets. 

This query is useful, for example, to analyze patterns in web traffic by sampling IP addresses into manageable groups while maintaining consistency - the same IP address will always hash to the same group. This can help identify behavioral patterns or anomalies in subsets of your traffic. 

Sample output from the incoming example data: 

_hash| _count  
---|---  
2| 1  
3| 1  
6| 1  
8| 3  
9| 1  
  
Note that the hash values remain consistent for the same input, enabling reliable sampling across time periods. 

#### Generate Different But Consistent Hash Values From Same Input Data

**Generate different but consistent hash values from the same input data using the[`hash()`](functions-hash.html "hash\(\)") function with seed **

##### Query

logscale
    
    
    hash(field=user_id, limit=5, as="hash1")
    | hash(field=user_id, limit=5, seed=10, as="hash2")
    | hash(field=user_id, limit=5, seed=20, as="hash3")

##### Introduction

In this example, the [`hash()`](functions-hash.html "hash\(\)") function is used with different _`seed`_ values to demonstrate how the same input data can generate different hash values. This is useful when you need multiple independent but consistent ways to group or sample the same data. 

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
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         hash(field=user_id, limit=5, as="hash1")

Creates hash values from the user_id field and returns the results in the field hash1. 

  3. logscale
         
         | hash(field=user_id, limit=5, seed=10, as="hash2")

Creates a second set of hash values from the same user_id field but uses a _`seed`_ value of `10` and returns the results in the field hash2. Using a different seed value creates a different but equally consistent distribution of hash values. 

  4. logscale
         
         | hash(field=user_id, limit=5, seed=20, as="hash3")

Creates a third set of hash values using a _`seed`_ value of `20` and returns the results in the field hash3. This demonstrates how different seed values create different hash distributions for the same input data. 

  5. Event Result set.




##### Summary and Results

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




#### Hash a Field Using Different Seeds

**Generate hash values using the[`hash()`](functions-hash.html "hash\(\)") function with different seeds **

##### Query

logscale
    
    
    | hash_seed10 := hash(field=[username], seed=10)
    | hash_seed20 := hash(field=[username], seed=20)

##### Introduction

In this example, the [`hash()`](functions-hash.html "hash\(\)") function is used to demonstrate how different seed values affect the hash output while maintaining consistency for the same input values. 

Example incoming data might look like this: 

@timestamp| username| action  
---|---|---  
2025-08-27T08:51:51.312Z| alice| login  
2025-08-27T09:15:22.445Z| bob| login  
2025-08-27T10:30:15.891Z| alice| logout  
2025-08-27T11:45:33.167Z| charlie| login  
2025-08-27T12:20:44.723Z| bob| logout  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | hash_seed10 := hash(field=[username], seed=10)
         | hash_seed20 := hash(field=[username], seed=20)

Creates two new fields with different hash values for the same input: 

     * Field hash_seed10 contains hash values generated with `seed=10`

     * Field hash_seed20 contains hash values generated with `seed=20`

The [_`field`_](functions-hash.html#query-functions-hash-field) parameter specifies [username](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) as the input field in an array format. The [_`seed`_](functions-hash.html#query-functions-hash-seed) parameter initializes the hashing algorithm with different values, producing different but consistent hash patterns. 

  3. Event Result set.




##### Summary and Results

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
