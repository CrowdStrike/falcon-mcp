# math:log2() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-log2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:log2()`](functions-math-log2.html "math:log2\(\)")

Calculates the base 2 logarithm of a double field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-log2.html#query-functions-math-log2-as)|  string| optional[a] | `_log2`|  The name of the output field.   
[_`field`_](functions-math-log2.html#query-functions-math-log2-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-log2.html#query-functions-math-log2-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-log2.html#query-functions-math-log2-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:log2("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:log2(field="value")
> 
> These examples show basic structure only.
