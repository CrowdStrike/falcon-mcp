# math:pow() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-pow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:pow()`](functions-math-pow.html "math:pow\(\)")

Calculates the field value to the exponent power, that is, `fieldexponent`. It supports decimal values. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-pow.html#query-functions-math-pow-as)|  string| optional[a] | `_pow`|  The name of the output field.   
[_`exponent`_](functions-math-pow.html#query-functions-math-pow-exponent)|  number| required |  |  The exponent to use, for example, exp in xexp.   
[_`field`_](functions-math-pow.html#query-functions-math-pow-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-pow.html#query-functions-math-pow-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-pow.html#query-functions-math-pow-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:pow("value",exponent="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:pow(field="value",exponent="value")
> 
> These examples show basic structure only.

### [`math:pow()`](functions-math-pow.html "math:pow\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Power of Values

**Calculate values raised to a power using the[`math:pow()`](functions-math-pow.html "math:pow\(\)") function **

##### Query

logscale
    
    
    x := 2
    exp := 3
    | math:pow(field=x, exponent=exp, as=result)

##### Introduction

In this example, the [`math:pow()`](functions-math-pow.html "math:pow\(\)") function is used to calculate values raised to different powers (xexp), demonstrating both integer and decimal exponents. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 2
         exp := 3

Assigns the value `2` to field x (the value to be raised to a power) and `3` to field exp (the exponent). This will calculate `x3`, which equals `8`. 

  3. logscale
         
         | math:pow(field=x, exponent=exp, as=result)

Raises the value in the field x to the power specified by the [_`exponent`_](functions-math-pow.html#query-functions-math-pow-exponent) parameter and returns the result in a field named result. If the [_`as`_](functions-math-pow.html#query-functions-math-pow-as) parameter is not specified, the result is returned in a field named _pow as default. 

  4. Event Result set.




##### Summary and Results

The query calculates the power of a number by raising it to a specified exponent. The [`math:pow()`](functions-math-pow.html "math:pow\(\)") function supports both integer and decimal values, making it versatile for various mathematical calculations. For example, you can calculate squares (x2), cubes (x3), or roots (using fractional exponents like `0.5` for square root). 

This query is useful for exponential calculations, geometric computations, scientific notation conversions, and any scenario requiring power operations. The function handles positive and negative numbers, as well as decimal exponents. 

Sample output from the incoming example data: 

result  
---  
8.000000  
  
The result shows that `2` raised to the power of `3` (`2³`) equals `8`, demonstrating the basic power operation. The function can also handle more complex calculations like `2.5⁴` or `3⁻²`.
