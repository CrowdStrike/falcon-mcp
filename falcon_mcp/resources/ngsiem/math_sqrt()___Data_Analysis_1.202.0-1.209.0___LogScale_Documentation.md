# math:sqrt() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-sqrt.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:sqrt()`](functions-math-sqrt.html "math:sqrt\(\)")

Calculates the rounded positive square root of a double field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-sqrt.html#query-functions-math-sqrt-as)|  string| optional[a] | `_sqrt`|  The name of the output field.   
[_`field`_](functions-math-sqrt.html#query-functions-math-sqrt-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-sqrt.html#query-functions-math-sqrt-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-sqrt.html#query-functions-math-sqrt-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:sqrt("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:sqrt(field="value")
> 
> These examples show basic structure only.

### [`math:sqrt()`](functions-math-sqrt.html "math:sqrt\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Rounded Square Root Values

**Find and round square roots using the[`math:sqrt()`](functions-math-sqrt.html "math:sqrt\(\)") function **

##### Query

logscale
    
    
    myvalue := 100
    | math:sqrt(myvalue, as=square_root)

##### Introduction

In this example, the [`math:sqrt()`](functions-math-sqrt.html "math:sqrt\(\)") function is used to calculate the square root of an assigned value. The input must be a numeric field that can contain decimal values (floating-point numbers). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         myvalue := 100

Assigns the value `100` to a field named myvalue. This creates a new field with a constant value that will be used for the square root calculation. 

  3. logscale
         
         | math:sqrt(myvalue, as=square_root)

Takes the square root of the value in the myvalue field and returns the result in a new field named square_root. The function automatically rounds the result to the nearest integer. In this case, it calculates the square root of `100`, which is `10`. 

Note that - if not returning an exact integer, the function rounds the result to the nearest integer in case of non-perfect squares. For example: 

Square root of `90 = 9.487` rounds to `9`. 

Square root of `91 = 9.539` rounds to `10`. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate the square root of an assigned constant value, demonstrating how to combine value assignment with mathematical functions. 

This query is useful, for example, to perform calculations on fixed values or to add reference calculations to existing event data. 

Sample output from the incoming example data: 

square_root  
---  
10
