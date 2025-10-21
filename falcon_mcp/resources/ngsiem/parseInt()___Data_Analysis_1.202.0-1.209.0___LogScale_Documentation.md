# parseInt() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parseint.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseInt()`](functions-parseint.html "parseInt\(\)")

Converts an integer from any radix (or number base), such as from hexadecimal or octal, to `base=10`, the decimal radix, expected as input by all other functions. For example, converting the hexadecimal `FF` to `255` using `radix=16` or `77` to `63` using `radix=8`. The conversion is always unsigned. 

If the input fields has a prefix (other than `0x` and `16#`) then use [`regex()`](functions-regex.html "regex\(\)") to remove the prefix before using parseInt(). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-parseint.html#query-functions-parseint-as)|  string| optional[a] |  |  The output name of the field to set (defaults to the same as the input field).   
[_`endian`_](functions-parseint.html#query-functions-parseint-endian)|  string| optional[[a]](functions-parseint.html#ftn.table-functions-parseint-optparamfn) | `big`|  Input Digit-pair ordering (little, big) for hexadecimal.   
[_`field`_](functions-parseint.html#query-functions-parseint-field)[b]| string| required |  |  The name of the input field.   
[_`radix`_](functions-parseint.html#query-functions-parseint-radix)|  number| optional[[a]](functions-parseint.html#ftn.table-functions-parseint-optparamfn) | `16`|  Input Integer base (2 to 36).   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-parseint.html#query-functions-parseint-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parseint.html#query-functions-parseint-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseInt("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseInt(field="value")
> 
> These examples show basic structure only.

### [`parseInt()`](functions-parseint.html "parseInt\(\)") Syntax Examples

Shows how to parse a hexadecimal string in little endian as an integer. An input event with the field hexval with the value 8001 results in the field centigrades having the value `(1*256)+128=384`. 

logscale
    
    
    parseInt(hexval, as="centigrades", radix="16", endian="little")

Shows how to parse a hexadecimal string in big endian as an integer. An input event with the field hexval with the value 8001 results in the field centigrades having the value `(128*256)+1=32769`. 

logscale
    
    
    parseInt(hexval, as="centigrades", radix="16", endian="big")

Shows how to parse a binary string as an integer. An input event with the field bitval with the value `00011001` results in the field flags having the value `16+8+1=25`. 

logscale
    
    
    parseInt(bitval, as="flags", radix="2")
