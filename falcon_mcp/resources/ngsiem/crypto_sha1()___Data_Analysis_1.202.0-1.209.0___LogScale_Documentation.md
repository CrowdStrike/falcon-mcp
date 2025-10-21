# crypto:sha1() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-crypto-sha1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)")

Computes a cryptographic SHA1-hashing of the given input field or array of fields. The hashed output is returned as a `hex` string, meaning the hexadecimal representation of the SHA1 hash of data. 

This function can be used to calculate checksums to compare outside of LogScale or collect multiple fields into a combined string of fixed length. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-crypto-sha1.html#query-functions-crypto-sha1-as)|  string| optional[a] | `_sha1`|  The name of the output field.   
[_`field`_](functions-crypto-sha1.html#query-functions-crypto-sha1-field)[b]| array of strings| required |  |  The name of the field or fields to hash.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-crypto-sha1.html#query-functions-crypto-sha1-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-crypto-sha1.html#query-functions-crypto-sha1-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     crypto:sha1(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     crypto:sha1(field=["value"])
> 
> These examples show basic structure only.

### [`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") Function Operation

[`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") hashes the UTF-8 encoding of the fields. 

When providing more than one field: 

  * The function hashes the concatenation of the fields. 

  * If a given field is missing from an event — or if it has an empty value — it is treated as the empty string. 




### [`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") Examples

Click + next to an example below to get the full details.

#### SHA-1 Hash Multiple Fields

**SHA-1 hash multiple fields using the[`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") function **

##### Query

logscale
    
    
    crypto:sha1(field=[a,b,c])

##### Introduction

In this example, the [`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") function is used to hash the fields a,b,c and return the result into a field named `_sha1`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         crypto:sha1(field=[a,b,c])

Performs a cryptographic SHA1-hashing of a,b,c. The _`field`_ argument can be omitted to write: [`crypto:sha1([a,b,c])`](functions-crypto-sha1.html "crypto:sha1\(\)")

  3. Event Result set.




##### Summary and Results

The query is used to encode a string using the SHA-1 hash. When called with multiple values, [`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") function creates a single SHA-1 sum from the combined value of the supplied fields. Combining fields in this way and converting to an SHa-1 can be an effective method of creating a unique ID for a given fieldset which could be used to identify a specific event type. The SHA-1 is reproducible (for example, supplying the same values will produce the same SHA-1 sum), and so it can sometimes be an effective method of creating unique identifier or lookup fields for a [`join()`](functions-join.html "join\(\)") across two different datasets. 

#### SHA-1 Hash a Field With a Given Value

**SHA-1 hash a field with a given value using the[`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") function **

##### Query

logscale
    
    
    a := "Hello, world!"
    | crypto:sha1(a)

##### Introduction

In this example, the [`crypto:sha1()`](functions-crypto-sha1.html "crypto:sha1\(\)") function is used to hash the field a with value `Hello, world!` and convert the result into `_sha1`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         a := "Hello, world!"

Assigns the value `Hello, world!` to the field a. 

  3. logscale
         
         | crypto:sha1(a)

Performs a cryptographic SHA-1-hashing of a:= "Hello, world!". The output value would be `_sha1 = "943a702d06f34599aee1f8da8ef9f7296031d699"`

  4. Event Result set.




##### Summary and Results

The query is used to encode a string using the SHA-1 hash. The hash generators `MD5`, `SHA-1`, and `SHA-256` are, for example, useful for encoding passwords or representing other strings in the system as hashed values.
