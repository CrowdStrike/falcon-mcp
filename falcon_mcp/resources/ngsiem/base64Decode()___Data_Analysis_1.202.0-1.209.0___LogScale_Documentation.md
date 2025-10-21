# base64Decode() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-base64decode.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`base64Decode()`](functions-base64decode.html "base64Decode\(\)")

Performs Base64 decoding of a field. The decoded value is subsequently decoded as binary representation of a string according to the [_`charset`_](functions-base64decode.html#query-functions-base64decode-charset) parameter. To work with actual binary data, use `ISO-8859-1` character set. 

To reverse the decoding, use the [`base64Encode()`](functions-base64encode.html "base64Encode\(\)") function: 
    
    
    base64Encode(a, as=a) | base64Decode(field=a, as=a)

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-base64decode.html#query-functions-base64decode-as)|  string| optional[a] | `_base64Decode`|  Name of the field in which to store the decoded value.   
[_`charset`_](functions-base64decode.html#query-functions-base64decode-charset)|  string| optional[[a]](functions-base64decode.html#ftn.table-functions-base64decode-optparamfn) | [`UTF-8`](functions-base64decode.html#query-functions-base64decode-charset-option-utf-8)|  The character set to use when transforming bytes to string.   
|  |  | **Values**  
|  |  | [`ISO-8859-1`](functions-base64decode.html#query-functions-base64decode-charset-option-iso-8859-1)|   
|  |  | [`UTF-16BE`](functions-base64decode.html#query-functions-base64decode-charset-option-utf-16be)|   
|  |  | [`UTF-16LE`](functions-base64decode.html#query-functions-base64decode-charset-option-utf-16le)|   
|  |  | [`UTF-8`](functions-base64decode.html#query-functions-base64decode-charset-option-utf-8)|   
[ _`field`_](functions-base64decode.html#query-functions-base64decode-field)[b]| string| required |  |  The field on which to decode Base64 values.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-base64decode.html#query-functions-base64decode-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-base64decode.html#query-functions-base64decode-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     base64Decode("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     base64Decode(field="value")
> 
> These examples show basic structure only.

### Behavior on Invalid Encoding

An input field that does not contain a valid Base64 encoding may result in the following behavior: 

  * Characters outside the base encoding alphabet are ignored. 

  * If the base encoding is invalid, the output field is not created. 

  * When decoding to a code point that is invalid with respect to the selected charset, the invalid code point is replaced with a placeholder character. 




### [`base64Decode()`](functions-base64decode.html "base64Decode\(\)") Examples

Click + next to an example below to get the full details.

#### Perform Base64 Decoding of a Field

**Perform Base64 decoding of a field using[`base64Decode()`](functions-base64decode.html "base64Decode\(\)") function **

##### Query

logscale
    
    
    decoded := base64Decode(encoded)

##### Introduction

In this example, the [`base64Decode()`](functions-base64decode.html "base64Decode\(\)") function is used to manipulate character strings that are base64 encoded and return a base64-decoded version of the input string. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         decoded := base64Decode(encoded)

Decodes the `Base64` value in encoded and stores it in the field decoded (the field on which to decode `Base64` values). The decoded value is subsequently decoded as binary representation of a string according to the [_`charset`_](functions-base64decode.html#query-functions-base64decode-charset) parameter. The [_`charset`_](functions-base64decode.html#query-functions-base64decode-charset) parameter is the character set to use when transforming bytes to string. To work with binary data, use `ISO-8859-1` character set. 

  3. Event Result set.




##### Summary and Results

The query is used to filter on input fields that do not contain a valid Base64 encoding. When decoding to a code point that is invalid with respect to the selected charset, the invalid code point is replaced with a placeholder character. This process ensures that data can be easily processed by computers.
