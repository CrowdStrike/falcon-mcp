# math:log1p() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-log1p.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:log1p()`](functions-math-log1p.html "math:log1p\(\)")

Calculates the natural logarithm of the sum of field value and 1\. For small values of `x`, the result of `log1p(x)` is much closer to the true result of `ln(1 + x)` than the floating-point evaluation of `log(1.0+x)`. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-log1p.html#query-functions-math-log1p-as)|  string| optional[a] | `_log1p`|  The name of the output field.   
[_`field`_](functions-math-log1p.html#query-functions-math-log1p-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-log1p.html#query-functions-math-log1p-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-log1p.html#query-functions-math-log1p-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:log1p("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:log1p(field="value")
> 
> These examples show basic structure only.

### [`math:log1p()`](functions-math-log1p.html "math:log1p\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Natural Logarithm of Value Plus One

**Calculate the natural logarithm of`(1 + x)` using the [`math:log1p()`](functions-math-log1p.html "math:log1p\(\)") function **

##### Query

logscale
    
    
    x := 0.0001
    | math:log1p(x, as=log1p_result)

##### Introduction

In this example, the [`math:log1p()`](functions-math-log1p.html "math:log1p\(\)") function is used to demonstrate accurate calculation of `ln(1 + x)`, particularly for small values where standard floating-point arithmetic might lose precision. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 0.0001

Assigns a small value `0.0001` to a field named x. This demonstrates the function's precision advantage with small values. 

  3. logscale
         
         | math:log1p(x, as=log1p_result)

Calculates `ln(1 + x)` for the value in field x and returns the result in a new field named log1p_result. If the [_`as`_](functions-math-log1p.html#query-functions-math-log1p-as) parameter is not specified, the result is returned in a field named _log1p as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate `ln(1 + x)` with high precision, particularly beneficial for small values where standard floating-point calculations might be inaccurate. 

This query is useful, for example, when working with small incremental changes, calculating precise logarithmic values near 1, or in financial calculations involving rates close to zero. 

Sample output from the incoming example data: 

log1p_result  
---  
0.00009999999833333334  
  
The result demonstrates the precise calculation of `ln(1 + 0.0001)`. Note that for very small values, the result is close to, but not exactly equal to, the input value. This is because [`math:log1p()`](functions-math-log1p.html "math:log1p\(\)") provides better numerical accuracy than calculating `ln(1.0 + x)` directly, especially important when working with small values where floating-point precision matters.
