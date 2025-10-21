# math:ceil() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-ceil.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:ceil()`](functions-math-ceil.html "math:ceil\(\)")

Rounds the field value to the smallest (closest to negative infinity) double value that is greater than or equal to the field value and is equal to a mathematical integer. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-ceil.html#query-functions-math-ceil-as)|  string| optional[a] | `_ceil`|  The name of the output field.   
[_`field`_](functions-math-ceil.html#query-functions-math-ceil-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-ceil.html#query-functions-math-ceil-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-ceil.html#query-functions-math-ceil-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:ceil("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:ceil(field="value")
> 
> These examples show basic structure only.

### [`math:ceil()`](functions-math-ceil.html "math:ceil\(\)") Examples

Click + next to an example below to get the full details.

#### Round Numbers Up to Nearest Integer

**Round a number up to the nearest integer using the[`math:ceil()`](functions-math-ceil.html "math:ceil\(\)") function **

##### Query

logscale
    
    
    x := 3.1
    | math:ceil(x, as=result)

##### Introduction

In this example, the [`math:ceil()`](functions-math-ceil.html "math:ceil\(\)") function is used to demonstrate ceiling rounding behavior with a decimal number, showing how it always rounds up to the next integer regardless of the decimal value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 3.1

Assigns the double-precision floating-point value `3.1` to a field named x. This value will demonstrate how ceiling rounding always rounds up to the next integer, even with a small decimal portion. 

  3. logscale
         
         | math:ceil(x, as=result)

Rounds up the value in field x to the nearest integer and returns the result in a new field named result. If the [_`as`_](functions-math-ceil.html#query-functions-math-ceil-as) parameter is not specified, the result is returned in a field named _ceil as default. 

  4. Event Result set.




##### Summary and Results

The query is used to round numbers up to the nearest integer, which is useful when you need to ensure values are not underestimated or when working with whole units that cannot be fractional. 

This query is useful, for example, to calculate minimum container needs, determine upper bounds for resource allocation, or round up time durations to whole units. 

Sample output from the incoming example data: 

result  
---  
4.0  
  
The result shows that `math:ceil(3.1) = 4.0`, demonstrating how the function always rounds up to the next integer regardless of the decimal portion. 

Note that ceiling rounding has distinct behaviors for different types of numbers: positive numbers round up to the next integer, negative numbers round up toward zero, and integers remain unchanged. For example: `math:ceil(3.9) = 4.0`, `math:ceil(-3.1) = -3.0`, `math:ceil(5.0) = 5.0`.
