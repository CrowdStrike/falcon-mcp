# Security Related Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-security.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Security Related Query Functions

LogScale's security related query functions can be used to generate, or compare hashed values, obfuscate (hide) data, or validate data with CrowdStrike's IOC database. 

**Table: Security Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`hashMatch([bits], [field], [hash], input, salt)`](functions-hashmatch.html "hashMatch\(\)")| [_`input`_](functions-hashmatch.html#query-functions-hashmatch-input)|  |  Calculates a secure hash of a field and uses it to match events as a filter.   
[`hashRewrite([as], [bits], field, [hash], [replaceInRawstring], salt)`](functions-hashrewrite.html "hashRewrite\(\)")| [_`field`_](functions-hashrewrite.html#query-functions-hashrewrite-field)|  |  Calculates a secure hash of a field for storing in the event.   
[`ioc:lookup([confidenceThreshold], field, [include], [prefix], [strict], type)`](functions-ioc-lookup.html "ioc:lookup\(\)")| [_`field`_](functions-ioc-lookup.html#query-functions-ioc-lookup-field)|  |  Look up IOCs (Indicators of Compromise).   
  
  


LogScale operates with the security related functions [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") and [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)"), which can be used together to provide a solution for handling sensitive data. 

  * [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") converts sensitive values into secure hashes. 

  * [`hashMatch()`](functions-hashmatch.html "hashMatch\(\)") enables searching for hashed values stored or generated in events. 




Both functions use a _salt_ value (defined by the [_`salt`_](functions-hashmatch.html#query-functions-hashmatch-salt) parameter) that is used as a random string added to the data before hashing. The salt value allows for customized hash generation which may be required to hide or obfuscate data. 

### Understanding Salt in Security

Using a salt is crucial for enhancing the security of hashed values. When you hash sensitive data, for example, passwords, adding a salt value creates a controlled output hash, even for identical input values. In a typical hashing situation, [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") will create the same hash value for a given input string. But a salt value creates a customized hash value. This can be used to create a hash that can only be matched if the corresponding salt is used to generate the hash match. 

Consider three users who choose the same password: `password123`

  * **Without salt:**

The system hashes each password directly. All three users end up with identical hash values because they used the same password. This creates security vulnerabilities: 

    * Attackers can use pre-computed hash tables (rainbow tables) to crack passwords 

    * Common passwords are easy to identify by their hash values 

    * Users with identical passwords have matching hashes 

  * **With salt:**

The system adds a unique random string before hashing each password. This creates different hashes for identical passwords: 

    * Pre-computed hash tables become ineffective 

    * Each hash is unique, even for identical passwords 

    * Attackers must crack each hash individually 




#### Security Benefits of Salt

Salt provides these key security advantages: 

  * Makes identical input values produce different hashes when using different salts 

  * Prevents rainbow table attacks (prevents the use of precomputed rainbow tables to reverse the hashes) 

  * Makes password cracking more difficult 

  * Hides patterns in hashed data 

  * Adds security beyond basic hashing 




##### Example of hashing with or without salt

In the following is an example of why salt is important by comparing hashed passwords with and without salt: 

Example incoming data might look like this: 

@timestamp| user_id| password| action  
---|---|---|---  
2025-09-01T10:00:00Z| user1| password123| login  
2025-09-01T10:00:05Z| user2| password123| login  
2025-09-01T10:00:10Z| user3| 321password| login  
  
Without using a salt value - Vulnerable

Without a salt, identical passwords create identical hashes, which is vulnerable because: 

  * Attackers can use rainbow tables (pre-computed hash tables) to crack passwords. 

  * Common passwords are easily identified by their hash. 

  * Multiple users with the same password have identical hashes. 




With a salt value - secure

With a salt, security is improved because: 

  * Rainbow tables become ineffective (hash is unique due to the unique salt value used with the function). 

  * Identical passwords produce different hashes when using different salts. 

  * Brute-force attacks must be performed individually for each hash. 




Without a unique salt value, anybody intercepting the data or viewing the information would be able to use a brute force approach to guess the original password; because the [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") would compute the same value for a given password. By using a salt value, the event data will contain a hashed value computed from a combination of the salt and original password; without both pieces of information a brute force approach to guess the value will not work. 

The [_`salt`_](functions-hashrewrite.html#query-functions-hashrewrite-salt) is required by [`hashRewrite()`](functions-hashrewrite.html "hashRewrite\(\)") for this reason. The value must be a string, not a field value, and so the same salt value will be used for each event in the query. However, without knowing the salt value used in the query, the returned hash is more complex and unique and, therefore, more secure. 

For example, when using this query: 

logscale
    
    
    hashRewrite(field=password,salt="unique_salt_2025")

The output might look like this: 

@timestamp| user_id| password| action  
---|---|---|---  
2025-09-01T10:00:00Z| user1| II9E7p6TOH7NeJz0efBARcboLc94SdQYq5aUZR8ipD4| login  
2025-09-01T10:00:05Z| user2| II9E7p6TOH7NeJz0efBARcboLc94SdQYq5aUZR8ipD4| login  
2025-09-01T10:00:10Z| user3| O6sZLJM3K2zewis2ZjhVtoed8tzRp7tlINZX5XD9Vm0| login  
  
The hashed value for `user1` and `user2` will be returned as the same value, as the salt and original password are consistent even though the user IDs are different.

The example demonstrates the security implications of using or omitting salt when hashing data. This comparison is useful for understanding why proper salt usage is crucial for security.
