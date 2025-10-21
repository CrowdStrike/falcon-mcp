# math:log10() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-log10.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:log10()`](functions-math-log10.html "math:log10\(\)")

Calculates the base 10 logarithm of a double field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-log10.html#query-functions-math-log10-as)|  string| optional[a] | `_log10`|  The name of the output field.   
[_`field`_](functions-math-log10.html#query-functions-math-log10-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-log10.html#query-functions-math-log10-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-log10.html#query-functions-math-log10-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:log10("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:log10(field="value")
> 
> These examples show basic structure only.

### [`math:log10()`](functions-math-log10.html "math:log10\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Base 10 Logarithm of Values

**Calculate the base 10 logarithm of a double field using the[`math:log10()`](functions-math-log10.html "math:log10\(\)") function **

##### Query

logscale
    
    
    x := 100.0
            | math:log10(x, as=log10_result)

##### Introduction

In this example, the [`math:log10()`](functions-math-log10.html "math:log10\(\)") function is used to calculate the base 10 logarithm of a double-precision value, showing how many times you need to multiply 10 by itself to get that value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 100.0

Assigns the double-precision floating-point value `100.0` to a field named x. This value will be used to calculate its base 10 logarithm. Note the decimal point indicating a floating-point number. 

  3. logscale
         
         | math:log10(x, as=log10_result)

Calculates the base 10 logarithm of the double-precision value in field x and returns the result in a new field named log10_result as a double-precision number. If the [_`as`_](functions-math-log10.html#query-functions-math-log10-as) parameter is not specified, the result is returned in a field named _log10 as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate the base 10 logarithm of a double-precision value, which is useful in analyzing exponential growth or decay in decimal systems. 

This query is useful, for example, to analyze orders of magnitude in scientific notation, convert between linear and logarithmic scales, or measure exponential relationships in scientific applications where precise floating-point calculations are required. 

Sample output from the incoming example data: 

log10_result  
---  
2.000000  
  
The result shows that the base 10 logarithm of `100.0 = 2.000000`, meaning that `10² = 100`. This indicates that you need to multiply 10 by itself 2 times to get 100. 

Some other examples with double-precision values: 

  * base 10 logarithm of 10.0 = 1.000000 (`10¹ = 10`) 

  * base 10 logarithm of 1000.0 = 3.000000 (`10³ = 1000`) 

  * base 10 logarithm of 1.0 = 0.000000 (`10⁰ = 1`) 

  * base 10 logarithm of 0.1 = -1.000000 (`10⁻¹ = 0.1`)
