# base64Encode() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-base64encode.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`base64Encode()`](functions-base64encode.html "base64Encode\(\)")

Performs Base64 encoding of a field as `UTF-8`. This encoding ensures that values containing special characters (for example emojis or `@`) are converted to a set of known, non-special characters. 

To reverse the encoding, use the [`base64Decode()`](functions-base64decode.html "base64Decode\(\)") function: 
    
    
    base64Encode(a, as=a) | base64Decode(field=a, as=a)

This sequence of operations produces an event where field a retains its original value. For more information about the reverse operation, see [`base64Decode()`](functions-base64decode.html "base64Decode\(\)"). 

### Note

The [`base64Encode()`](functions-base64encode.html "base64Encode\(\)") function does not accept a _`charset`_ parameter, and all input strings are encoded as `UTF-8`. This behavior differs from [`base64Decode()`](functions-base64decode.html "base64Decode\(\)"), which allows charset specification. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-base64encode.html#query-functions-base64encode-as)|  string| optional[a] | `_base64Encode`|  Name of the field in which to store the encoded value.   
[_`field`_](functions-base64encode.html#query-functions-base64encode-field)[b]| string| required |  |  The field on which to encode Base64 values.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-base64encode.html#query-functions-base64encode-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-base64encode.html#query-functions-base64encode-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     base64Encode("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     base64Encode(field="value")
> 
> These examples show basic structure only.

### [`base64Encode()`](functions-base64encode.html "base64Encode\(\)") Examples

Click + next to an example below to get the full details.

#### Perform Base64 Encoding of a Field

**Perform Base64 encoding of a field using the[`base64Encode()`](functions-base64encode.html "base64Encode\(\)") function **

##### Query

logscale
    
    
    base64Encode(a)

##### Introduction

In this example, the [`base64Encode()`](functions-base64encode.html "base64Encode\(\)") function is used to manipulate input string that are `UTF-8` encoded and return a base64-encoded version of the input string in field a in a new field named _base64Encode. The input string is: `Hello, World!`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         base64Encode(a)

Takes the input string `Hello, World!` in field a, converts the string to UTF-8 encoding, and then encodes this string with Base64. 

The output value would be `_base64Encode = "SGVsbG8sIFdvcmxkIQ=="`

It is also possible to use an [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter to specify another output field than the default _base64Encode: [`base64Encode(a, as=out)`](functions-base64encode.html "base64Encode\(\)")

  3. Event Result set.




##### Summary and Results

The [`base64Encode()`](functions-base64encode.html "base64Encode\(\)") function is used to encode strings that may contain special characters, to be able to transmit or store these, and later be decoded using the [`base64Decode()`](functions-base64decode.html "base64Decode\(\)") function if needed. The query converts data into a format suitable for systems that only accept ASCII characters. This process ensures that data can be easily processed by computers. 

A reverse of the encoding is performed using this query: `base64Encode(a, as=a) | base64Decode(field=a, as=a) `

Note that while Base64 encoding is useful for data handling, it is not a secure encryption method.
