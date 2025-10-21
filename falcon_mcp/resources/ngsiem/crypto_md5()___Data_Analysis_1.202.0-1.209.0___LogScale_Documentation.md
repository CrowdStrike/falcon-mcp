# crypto:md5() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-crypto-md5.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)")

Computes a cryptographic MD5-hashing of an input string of one field or an array of fields. The hashed output is returned as a `hex` string, meaning the hexadecimal representation of the MD5 hash of data. 

This function can be used to calculate checksums to compare outside of LogScale or collect multiple fields into a combined string of fixed length. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-crypto-md5.html#query-functions-crypto-md5-as)|  string| optional[a] | `_md5`|  The name of the output field.   
[_`field`_](functions-crypto-md5.html#query-functions-crypto-md5-field)[b]| array of strings| required |  |  The name of the field or fields to hash.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-crypto-md5.html#query-functions-crypto-md5-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-crypto-md5.html#query-functions-crypto-md5-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     crypto:md5(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     crypto:md5(field=["value"])
> 
> These examples show basic structure only.

### [`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") Function Operation

[`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") hashes the UTF-8 encoding of the fields. 

When providing more than one field: 

  * The function hashes the concatenation of the fields. 

  * If a given field is missing from an event — or if it has an empty value — it is treated as the empty string. 




### [`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") Examples

Click + next to an example below to get the full details.

#### MD5 Hash Multiple Fields

**MD5 hash multiple fields using the[`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") function **

##### Query

logscale
    
    
    crypto:md5(field=[a,b,c])

##### Introduction

In this example, the [`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") function is used to hash the fields a,b,c and return the result into a field named `_md5`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         crypto:md5(field=[a,b,c])

Performs a cryptographic MD5-hashing of a,b,c. The _`field`_ argument can be omitted to write: [`crypto:md5([a,b,c])`](functions-crypto-md5.html "crypto:md5\(\)")

  3. Event Result set.




##### Summary and Results

The query is used to encode a string using the MD5 hash. When called with multiple values, [`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") function creates a single MD5 sum from the combined value of the supplied fields. Combining fields in this way and converting to an MD5 can be an effective method of creating a unique ID for a given fieldset which could be used to identify a specific event type. The MD5 is reproducible (for example, supplying the same values will produce the same MD5 sum), and so it can sometimes be an effective method of creating unique identifier or lookup fields for a [`join()`](functions-join.html "join\(\)") across two different datasets. 

#### MD5 Hash a Field With a Given Value

**MD5 hash a field with a given value using the[`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") function **

##### Query

logscale
    
    
    a := "Hello, world!"
    | crypto:md5(a)

##### Introduction

In this example, the [`crypto:md5()`](functions-crypto-md5.html "crypto:md5\(\)") function is used to hash the field a with value `Hello, world!` and convert the result into `_md5`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         a := "Hello, world!"

Assigns the value `Hello, world!` to the field a. 

  3. logscale
         
         | crypto:md5(a)

Performs a cryptographic MD5-hashing of a:= "Hello, world!". The output value would be `_md5 = "6cd3556deb0da54bca060b4c39479839"`

  4. Event Result set.




##### Summary and Results

The query is used to encode a string using the MD5 hash. The hash generators `MD5`, `SHA-1`, and `SHA-256` are, for example, useful for encoding passwords or representing other strings in the system as hashed values.
