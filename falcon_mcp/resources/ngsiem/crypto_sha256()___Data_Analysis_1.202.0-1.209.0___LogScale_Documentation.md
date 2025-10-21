# crypto:sha256() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-crypto-sha256.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)")

Computes a cryptographic SHA256-hashing of the given input field or array of fields. The hashed output is returned as a `hex` string, meaning the hexadecimal representation of the SHA256 hash of data. 

This function can be used to calculate checksums to compare outside of LogScale or collect multiple fields into a combined string of fixed length. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-crypto-sha256.html#query-functions-crypto-sha256-as)|  string| optional[a] | `_sha256`|  The name of the output field.   
[_`field`_](functions-crypto-sha256.html#query-functions-crypto-sha256-field)[b]| array of strings| required |  |  The name of the field or fields to hash.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-crypto-sha256.html#query-functions-crypto-sha256-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-crypto-sha256.html#query-functions-crypto-sha256-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     crypto:sha256(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     crypto:sha256(field=["value"])
> 
> These examples show basic structure only.

### [`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") Function Operation

[`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") hashes the UTF-8 encoding of the fields. 

When providing more than one field: 

  * The function hashes the concatenation of the fields. 

  * If a given field is missing from an event — or if it has an empty value — it is treated as the empty string. 




### [`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") Examples

Click + next to an example below to get the full details.

#### SHA-256 Hash Multiple Fields

**SHA-256 hash multiple fields using the[`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") function **

##### Query

logscale
    
    
    crypto:sha256(field=[a,b,c])

##### Introduction

In this example, the [`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") function is used to hash the fields a,b,c and return the result into a field named `_sha256`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         crypto:sha256(field=[a,b,c])

Performs a cryptographic SHA256-hashing of a,b,c. The _`field`_ argument can be omitted to write: [`crypto:sha1([a,b,c])`](functions-crypto-sha1.html "crypto:sha1\(\)")

  3. Event Result set.




##### Summary and Results

The query is used to encode a string using the SHA-256 hash. When called with multiple values, [`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") function creates a single SHA-256 sum from the combined value of the supplied fields. Combining fields in this way and converting to an SHa-256 can be an effective method of creating a unique ID for a given fieldset which could be used to identify a specific event type. The SHA-256 is reproducible (for example, supplying the same values will produce the same SHA-256 sum), and so it can sometimes be an effective method of creating unique identifier or lookup fields for a [`join()`](functions-join.html "join\(\)") across two different datasets. 

#### SHA-256 Hash a Field With a Given Value

**SHA-256 hash a field with a given value using the[`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") function **

##### Query

logscale
    
    
    a := "Hello, world!"
    | crypto:sha256(a)

##### Introduction

In this example, the [`crypto:sha256()`](functions-crypto-sha256.html "crypto:sha256\(\)") function is used to hash the field a with value `Hello, world!` and convert the result into `_sha256`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         a := "Hello, world!"

Assigns the value `Hello, world!` to the field a. 

  3. logscale
         
         | crypto:sha256(a)

Performs a cryptographic SHA-256-hashing of a:= "Hello, world!". The output value would be `_sha256 = "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3"`

  4. Event Result set.




##### Summary and Results

The query is used to encode a string using the SHA-256 hash. The hash generators `MD5`, `SHA-1`, and `SHA-256` are, for example, useful for encoding passwords or representing other strings in the system as hashed values.
