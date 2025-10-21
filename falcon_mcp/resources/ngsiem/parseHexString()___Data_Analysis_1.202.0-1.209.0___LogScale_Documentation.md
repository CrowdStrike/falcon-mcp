# parseHexString() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsehexstring.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseHexString()`](functions-parsehexstring.html "parseHexString\(\)")

Parses the input from hex encoded bytes, decoding the resulting bytes as a string using the selected character set. If the input fields has a prefix (other than 0x and 16#) then use [`regex()`](functions-regex.html "regex\(\)") or [`replace()`](functions-replace.html "replace\(\)") to remove the prefix before using `parseHexString`. Any non-hex characters in the input are ignored — the decoding attempts to decode all chars in the field that match `0-9` or `A-F`. Case is ignored. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-parsehexstring.html#query-functions-parsehexstring-as)|  string| optional[a] | `_parsehexstring`|  Name of output field.   
[_`charset`_](functions-parsehexstring.html#query-functions-parsehexstring-charset)|  string| optional[[a]](functions-parsehexstring.html#ftn.table-functions-parsehexstring-optparamfn) | [`UTF-8`](functions-parsehexstring.html#query-functions-parsehexstring-charset-option-utf-8)|  The charset to use when transforming bytes to string.   
|  |  | **Values**  
|  |  | [`ISO-8859-1`](functions-parsehexstring.html#query-functions-parsehexstring-charset-option-iso-8859-1)|   
|  |  | [`UTF-16BE`](functions-parsehexstring.html#query-functions-parsehexstring-charset-option-utf-16be)|   
|  |  | [`UTF-16LE`](functions-parsehexstring.html#query-functions-parsehexstring-charset-option-utf-16le)|   
|  |  | [`UTF-8`](functions-parsehexstring.html#query-functions-parsehexstring-charset-option-utf-8)|   
[ _`field`_](functions-parsehexstring.html#query-functions-parsehexstring-field)[b]| string| required |  |  Specifies the field containing the hex string to use as input.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-parsehexstring.html#query-functions-parsehexstring-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parsehexstring.html#query-functions-parsehexstring-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseHexString("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseHexString(field="value")
> 
> These examples show basic structure only.

### [`parseHexString()`](functions-parsehexstring.html "parseHexString\(\)") Syntax Examples

Parses the string `48656c6c6f576f726c64` from the field named foo into the field text, getting the value Helloworld: 

logscale
    
    
    foo := 48656c6c6f576f726c64
    | parseHexString(foo, as=text, charset="ISO-8859-1")

Parses the string `0x4 865 6c6c6f576f726c6420 plus F 0 9 F 9 8 8 0` from the field named hex into the field text, using `UTF-8` and getting the value Helloworld 😀 where the smiley is the result of decoding the trailing digits: 

logscale
    
    
    hex := "0x4 865 6c6c6f576f726c6420 plus F 0 9 F 9 8 8 0"
    | text := parseHexString(hex)
