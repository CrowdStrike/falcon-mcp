# hashRewrite() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-hashrewrite.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)")

Calculates a secure hash of a field for storing in the event. See [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") on how to search for events using hashes. Bits can reduce the width of the output if desired to keep the resulting strings short. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-hashrewrite.html#query-functions-hashrewrite-as)|  string| optional[a] |  |  The name of output field, defaults to the input field.   
[_`bits`_](functions-hashrewrite.html#query-functions-hashrewrite-bits)|  integer| optional[[a]](functions-hashrewrite.html#ftn.table-functions-hashrewrite-optparamfn) | [`256`](functions-hashrewrite.html#query-functions-hashrewrite-bits-max-256)|  Hash algorithm output bits to keep. Must be a multiple of 8.   
|  | **Minimum**| `8`|   
|  | **Maximum**| [`256`](functions-hashrewrite.html#query-functions-hashrewrite-bits-max-256)|   
[ _`field`_](functions-hashrewrite.html#query-functions-hashrewrite-field)[b]| string| required |  |  The name of the field to hash.   
[_`hash`_](functions-hashrewrite.html#query-functions-hashrewrite-hash)|  string| optional[[a]](functions-hashrewrite.html#ftn.table-functions-hashrewrite-optparamfn) | [`sha256`](functions-hashrewrite.html#query-functions-hashrewrite-hash-option-sha256)|  Hash algorithm.   
|  |  | **Values**  
|  |  | [`sha256`](functions-hashrewrite.html#query-functions-hashrewrite-hash-option-sha256)|   
|  |  | [`sha512`](functions-hashrewrite.html#query-functions-hashrewrite-hash-option-sha512)|   
[ _`replaceInRawstring`_](functions-hashrewrite.html#query-functions-hashrewrite-replaceinrawstring)|  boolean| optional[[a]](functions-hashrewrite.html#ftn.table-functions-hashrewrite-optparamfn) | `true`|  Replace all substrings in [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) that has the input value with the hash too.   
[_`salt`_](functions-hashrewrite.html#query-functions-hashrewrite-salt)|  string| required |  |  The name of the secret salt to use.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-hashrewrite.html#query-functions-hashrewrite-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-hashrewrite.html#query-functions-hashrewrite-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     hashRewrite("value",salt="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     hashRewrite(field="value",salt="value")
> 
> These examples show basic structure only.

### [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") Syntax Examples

Replace the value in the ssn field with the hash of the existing value, also replacing it in [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring)

logscale
    
    
    hashRewrite(ssn, salt="salt1")

### [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") Examples

Click + next to an example below to get the full details.

#### Hash Field Values Using [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)")

**Hash sensitive data using the[`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") function with a [_`salt`_](functions-hashrewrite.html#query-functions-hashrewrite-salt) value **

##### Query

logscale
    
    
    hashRewrite(ssn, salt="salt1")

##### Introduction

In this example, the [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") function is used to hash Social Security Numbers (SSNs) using a specified salt value ([_`salt`_](functions-hashmatch.html#query-functions-hashmatch-salt) equal to `salt1`). 

Example incoming data might look like this: 

@timestamp| user_id| ssn| action  
---|---|---|---  
2025-09-01T10:00:00Z| user1| 123-45-6789| profile_update  
2025-09-01T10:00:05Z| user2| 123-45-6789| new_account  
2025-09-01T10:00:10Z| user3| 456-78-9012| profile_view  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         hashRewrite(ssn, salt="salt1")

Hashes the values in the ssn field through a multi-step process. First the [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") function takes each value in the ssn field and adds the [_`salt`_](functions-hashrewrite.html#query-functions-hashrewrite-salt) value `salt1` to it before hashing. The function then creates a hash of the combined value (original + salt) and replaces the original value with the resulting hash. 

Note that the salt value requires specific handling for security purposes. It must be kept consistent when searching for these values later, stored securely outside the log data, and should be different for different types of sensitive data. 

  3. Event Result set.




##### Summary and Results

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

The example demonstrates how to use [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") in LogScale to protect sensitive data while maintaining searchability. To search for specific SSNs in the hashed data, use [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") with the same salt value. 

After hashing sensitive data using this method, you can search for specific values using the [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") function.
