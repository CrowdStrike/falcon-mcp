# math:log() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-log.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:log()`](functions-math-log.html "math:log\(\)")

Calculates the natural logarithm (base e) of the value in a double field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-log.html#query-functions-math-log-as)|  string| optional[a] | `_log`|  The name of the output field.   
[_`field`_](functions-math-log.html#query-functions-math-log-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-log.html#query-functions-math-log-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-log.html#query-functions-math-log-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:log("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:log(field="value")
> 
> These examples show basic structure only.

### [`math:log()`](functions-math-log.html "math:log\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Natural Logarithm of Values

**Calculate the natural logarithm of a double field using the[`math:log()`](functions-math-log.html "math:log\(\)") function **

##### Query

logscale
    
    
    x := 7.389056099
    | math:log(x, as=log_result)

##### Introduction

In this example, the [`math:log()`](functions-math-log.html "math:log\(\)") function is used to calculate the natural logarithm of a double-precision value, showing how many times you need to multiply Euler's number `e` by itself to get that value. The value `e` is a transcendental number that serves as the base of natural logarithms and exponential functions. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 7.389056099

Assigns the double-precision floating-point value `7.389056099` to a field named x. This value will be used to calculate its natural logarithm. Note the decimal point indicating a floating-point number. 

  3. logscale
         
         | math:log(x, as=log_result)

Calculates the natural logarithm of the double-precision value in field x and returns the result in a new field named log_result as a double-precision number. If the [_`as`_](functions-math-log.html#query-functions-math-log-as) parameter is not specified, the result is returned in a field named _log as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate the natural logarithm of a double-precision value, which is useful in analyzing exponential growth or decay in natural systems. 

This query is useful, for example, to analyze natural growth patterns, normalize exponential data, or measure rates of continuous change where precise floating-point calculations are required. 

Sample output from the incoming example data: 

log_result  
---  
2.000000  
  
The result shows that the natural logarithm of `7.389056099 = 2.000000`, meaning that `e² 蝶 7.389056099`. This indicates that you need to multiply `e` by itself 2 times to get approximately `7.389056099`. 

Some other examples with double-precision values: 

  * natural logarithm of 1.0 = 0.000000 (`e⁰ = 1`) 

  * natural logarithm of 2.718281828 = 1.000000 (`e¹ = e`) 

  * natural logarithm of 20.085536923 = 3.000000 (`e³ 蝶 20.085536923`) 

  * natural logarithm of 0.367879441 = -1.000000 (`e⁻¹ 蝶 0.367879441`) 




Euler's number `e` is a fundamental mathematical constant discovered by the mathematician Leonhard Euler. It is irrational and transcendental, and appears naturally in many mathematical calculations, particularly those involving continuous compound interest, exponential growth, or decay. When used as the base for logarithms, it creates natural logarithms, which have the unique property that their derivative is `1/x`, making them especially useful in calculus and natural sciences.
