# hashMatch() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-hashmatch.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)")

Calculates a secure hash of a field and uses that to match events as a filter. See [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") on how get hashes into events. Bits must be set to the value applied when the hash was stored in the event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`bits`_](functions-hashmatch.html#query-functions-hashmatch-bits)|  integer| optional[a] | [`256`](functions-hashmatch.html#query-functions-hashmatch-bits-max-256)|  Hash algorithm output bits to keep. Must be a multiple of 8.   
|  | **Minimum**| `8`|   
|  | **Maximum**| [`256`](functions-hashmatch.html#query-functions-hashmatch-bits-max-256)|   
[ _`field`_](functions-hashmatch.html#query-functions-hashmatch-field)|  string| optional[[a]](functions-hashmatch.html#ftn.table-functions-hashmatch-optparamfn) |  |  The name of the field to look for an exact match against. If not set then [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) is searched for a matching substring.   
[_`hash`_](functions-hashmatch.html#query-functions-hashmatch-hash)|  string| optional[[a]](functions-hashmatch.html#ftn.table-functions-hashmatch-optparamfn) | [`sha256`](functions-hashmatch.html#query-functions-hashmatch-hash-option-sha256)|  Hash algorithm to use for the match.   
|  |  | **Values**  
|  |  | [`sha256`](functions-hashmatch.html#query-functions-hashmatch-hash-option-sha256)|   
|  |  | [`sha512`](functions-hashmatch.html#query-functions-hashmatch-hash-option-sha512)|   
[ _`input`_](functions-hashmatch.html#query-functions-hashmatch-input)[b]| string| required |  |  A constant value to hash and then apply as the search term.   
[_`salt`_](functions-hashmatch.html#query-functions-hashmatch-salt)|  string| required |  |  The name of the secret salt to use.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`input`_](functions-hashmatch.html#query-functions-hashmatch-input) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`input`_](functions-hashmatch.html#query-functions-hashmatch-input) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     hashMatch("value",salt="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     hashMatch(input="value",salt="value")
> 
> These examples show basic structure only.

### [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") Syntax Examples

Filter events to only match those that have the value in the `ssn` field equal to the hash of 12345678 

logscale
    
    
    ssn =~ hashMatch("12345678", salt="salt1")

Filter events to only match those that have the value of the hash of 12345678 somewhere in [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring)

logscale
    
    
    hashMatch("12345678", salt="salt1")

### [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") Examples

Click + next to an example below to get the full details.

#### Match Events Containing Specific Hash Values

**Match events containing a specific hashed value using the[`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") function **

##### Query

logscale
    
    
    hashMatch("456-78-9012", salt="salt1")

##### Introduction

In this example, the [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") function is used to find events where the value `456-78-9012` appears in the event data as a hash created with the [_`salt`_](functions-hashmatch.html#query-functions-hashmatch-salt) equal to `salt1`. 

Example incoming data might look like this: 

@timestamp| @rawstring  
---|---  
2025-09-01T10:00:00Z| User logged in with hash:C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8  
2025-09-01T10:00:05Z| Failed login attempt hash:C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8  
2025-09-01T10:00:10Z| Password reset requested hash:naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         hashMatch("456-78-9012", salt="salt1")

Filters events by checking if the hash of value `456-78-9012` (created using the salt `salt1`) appears anywhere in the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field. The function creates the hash using the provided value and salt, then searches for this hash pattern in the event data. 

  3. Event Result set.




##### Summary and Results

The query is used to filter events that contain a specific hashed value in their content. 

This query is useful, for example, to search for specific sensitive values in logs where the values have been hashed for security purposes, such as finding events related to a specific user ID or account number that has been hashed in the logs. 

Sample output from the incoming example data: 

@timestamp| @rawstring  
---|---  
2025-09-01T10:00:10Z| Password reset requested hash:naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ  
  
Note that the salt value must match the one used when the original hash was created in the data. The function searches for the hash pattern anywhere in the event data. 

This example shows how to search for hashed values anywhere in event data. For searching in specific fields, see [Match Hashed Values in Specific Fields](https://library.humio.com/examples/examples-hashmatch-filter-ssn.html). To understand how to create searchable hashed data, see [Hash Field Values Using `hashRewrite()` ](https://library.humio.com/examples/examples-hashrewrite-field-value.html). 

#### Match Hashed Values in Specific Fields

**Match events where a field equals a hashed value using the[`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") function **

##### Query

logscale
    
    
    ssn =~ hashMatch("456-78-9012", salt="salt1")

##### Introduction

In this example, the [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") function is used to filter events where the ssn field matches the hash of a specific value, using a specified [_`salt`_](functions-hashmatch.html#query-functions-hashmatch-salt) value for the hashing. A salt is a random string added to the data before hashing to make the hash more secure. 

Note that the example uses the [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") function with the comparison operator `=~` to match against a specific field. 

Example incoming data might look like this: 

@timestamp| action| ssn| user_id  
---|---|---|---  
2025-09-01T10:00:00Z| profile_update| C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8| user1  
2025-09-01T10:00:05Z| new_account| C4ZkaokbIUltItryWgtdRmIdCCnsWVhhrOg3GDrTkx8| user2  
2025-09-01T10:00:10Z| profile_view| naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ| user3  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         ssn =~ hashMatch("456-78-9012", salt="salt1")

Filters events where the ssn field value matches the hash of `456-78-9012`. The [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") function creates a hash using the specified string and [_`salt`_](functions-hashmatch.html#query-functions-hashmatch-salt) value (`salt1`), then compares it against the value in the ssn field. 

The [_`salt`_](functions-hashmatch.html#query-functions-hashmatch-salt) parameter is required and should match the salt used when the original data was hashed (in this case `salt1`). For more information, see [Hash Field Values Using `hashRewrite()` ](https://library.humio.com/examples/examples-hashrewrite-field-value.html). 

  3. Event Result set.




##### Summary and Results

The query is used to find events where a hashed field matches an expected value without exposing the original sensitive data. 

This query is useful, for example, to track specific user activities in logs where sensitive information like social security numbers are stored in hashed form for security compliance. 

Sample output from the incoming example data: 

@timestamp| action| ssn| user_id  
---|---|---|---  
2025-09-01T10:00:10Z| profile_view| naHQMPbzY6pLiFG8aiJzfxw5Gj4mLQ+bf2b0AJv8OPQ| user3  
  
Only events where the hashed value in ssn matches the hash of `456-78-9012` are included in the results. 

This example demonstrates searching for specific hashed values in a named field. For searching hashed values anywhere in event data, see [Match Events Containing Specific Hash Values](https://library.humio.com/examples/examples-hashmatch-filter.html). To learn how to create hashed values that can be searched this way, see [Hash Field Values Using `hashRewrite()` ](https://library.humio.com/examples/examples-hashrewrite-field-value.html).
