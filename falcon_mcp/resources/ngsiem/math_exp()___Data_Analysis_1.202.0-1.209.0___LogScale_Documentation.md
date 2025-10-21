# math:exp() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-exp.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:exp()`](functions-math-exp.html "math:exp\(\)")

Calculates Euler's number e raised to the power of a double value in a field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-exp.html#query-functions-math-exp-as)|  string| optional[a] | `_exp`|  The name of the output field.   
[_`field`_](functions-math-exp.html#query-functions-math-exp-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-exp.html#query-functions-math-exp-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-exp.html#query-functions-math-exp-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:exp("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:exp(field="value")
> 
> These examples show basic structure only.

### [`math:exp()`](functions-math-exp.html "math:exp\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate `e` Raised to Power

**Calculate`e^x` using the [`math:exp()`](functions-math-exp.html "math:exp\(\)") function **

##### Query

logscale
    
    
    x := 1.0
    | math:exp(x, as=result)

##### Introduction

In this example, the [`math:exp()`](functions-math-exp.html "math:exp\(\)") function is used to calculate `e^x` for a given value, demonstrating exponential growth calculation. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 1.0

Assigns the double-precision floating-point value `1.0` to a field named x. This value will demonstrate the calculation of `e^x`, which equals Euler's number itself. 

  3. logscale
         
         | math:exp(x, as=result)

Calculates `e^x` for the value in field x and returns the result in a new field named result. If the [_`as`_](functions-math-exp.html#query-functions-math-exp-as) parameter is not specified, the result is returned in a field named _exp as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate exponential values, which is fundamental in calculating compound growth, decay processes, and various scientific calculations. 

This query is useful, for example, to calculate compound interest, population growth, or radioactive decay where the rate of change is proportional to the current value. 

Sample output from the incoming example data: 

result  
---  
2.718281828459045  
  
The result shows that `e^x` equals Euler's number. While [`math:exp()`](functions-math-exp.html "math:exp\(\)") is suitable for most exponential calculations, for very small values of x where you need to calculate `e^x - 1`, consider using [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") instead for better numerical precision. For an example, see [Calculate `e` Raised to Power Minus One](https://library.humio.com/examples/examples-mathexpm1-calculate-exp-minus-one.html)

Note that this [`math:exp()`](functions-math-exp.html "math:exp\(\)") function calculates the full exponential value, making it ideal for general exponential calculations where x is not close to zero. For calculations involving very small values where you need to subtract 1 from the result, [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") provides better numerical precision. 

#### Calculate `e` Raised to Power Minus One

**Calculate`e^x - 1` using the [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") or [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") functions **

##### Query

logscale
    
    
    x := 0.00001
    | math:expm1(x, as=precise_result)
    | math:exp(x, as=standard_result)

##### Introduction

In this example, the [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") function and [`math:exp()`](functions-math-exp.html "math:exp\(\)") function are used to calculate `e^x - 1` for a small value of `x`, demonstrating the superior precision of [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") compared to using [`math:exp()`](functions-math-exp.html "math:exp\(\)") and subtracting `1`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 0.00001

Assigns a very small double-precision floating-point value `0.00001` to a field named x. This small value near zero demonstrates where [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") provides better numerical precision. 

  3. logscale
         
         | math:expm1(x, as=precise_result)

Calculates `e^x - 1` for the value in field x and returns the result in a new field named precise_result. If the [_`as`_](functions-math-expm1.html#query-functions-math-expm1-as) parameter is not specified, the result is returned in a field named _expm1 as default. 

  4. logscale
         
         | math:exp(x, as=standard_result)

Calculates `e^x` for the value in field x and returns the result in a new field named standard_result. If the [_`as`_](functions-math-exp.html#query-functions-math-exp-as) parameter is not specified, the result is returned in a field named _exp as default. 

  5. Event Result set.




##### Summary and Results

The query is used to calculate exponential values minus one with high precision, which is particularly important in scientific and financial calculations involving very small values. The [`math:exp(x)`](functions-math-exp.html "math:exp\(\)") function is also mentioned in this query to show that it is less precise due to floating-point rounding compared to the [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") function. 

The precise_result field contains the more accurate calculation using [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)"), while standard_result shows the result of using [`math:exp()`](functions-math-exp.html "math:exp\(\)") and subtracting `1`. 

This query is useful, for example, to calculate small percentage changes in financial applications, compute precise scientific measurements near baseline values and analyze small deviations in statistical data. 

Sample output from the incoming example data: 

precise_result| standard_result  
---|---  
0.0000100000050000017| 0.0000100000050000166  
  
The results show that [`math:expm1()`](functions-math-expm1.html "math:expm1\(\)") provides more precise calculations for small values. For values close to zero, the difference between the two methods becomes significant in applications requiring high precision. 

Note that while the difference between the two methods may appear small, it becomes crucial in applications requiring high precision, especially when dealing with very small values or when performing many successive calculations. 

In short, best practise is to: 

Use [`math:expm1(x)`](functions-math-expm1.html "math:expm1\(\)") instead of `[`math:exp(x)`](functions-math-exp.html "math:exp\(\)") - 1` when: 

  * x is close to 0 

  * Precision is important 

  * Working with small values 




Use [`math:exp(x)`](functions-math-exp.html "math:exp\(\)") \- 1 when: 

  * x is larger 

  * Extreme precision is not required 

  * Performance is more important than precision
