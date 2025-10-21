# math:floor() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-floor.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:floor()`](functions-math-floor.html "math:floor\(\)")

Rounds the field value to the largest (closest to positive infinity) double value that is less than or equal to the field value and is equal to a mathematical integer. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-floor.html#query-functions-math-floor-as)|  string| optional[a] | `_floor`|  The name of the output field.   
[_`field`_](functions-math-floor.html#query-functions-math-floor-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-floor.html#query-functions-math-floor-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-floor.html#query-functions-math-floor-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:floor("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:floor(field="value")
> 
> These examples show basic structure only.

### [`math:floor()`](functions-math-floor.html "math:floor\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Floor Value of a Number

**Calculate the largest integer less than or equal to a number using the[`math:floor()`](functions-math-floor.html "math:floor\(\)") function **

##### Query

logscale
    
    
    x := 3.7
    | math:floor(x, as=floor_result)

##### Introduction

In this example, the [`math:floor()`](functions-math-floor.html "math:floor\(\)") function is used to calculate the floor value of a decimal number, demonstrating how it always rounds down to the nearest integer regardless of the decimal portion. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 3.7

Assigns the double-precision floating-point value `3.7` to a field named x. This value will be used to demonstrate the floor function. Note the decimal point indicating a floating-point number. 

  3. logscale
         
         | math:floor(x, as=floor_result)

Calculates the floor value of the double-precision value in field x and returns the result in a new field named floor_result as a double-precision number. If the [_`as`_](functions-math-floor.html#query-functions-math-floor-as) parameter is not specified, the result is returned in a field named _floor as default. 

  4. Event Result set.




##### Summary and Results

The query is used to find the largest integer less than or equal to a given number, which is useful when you need to round numbers down consistently. 

This query is useful, for example, to calculate whole units from decimal measurements, determine complete time periods, or round down financial calculations where partial units are not allowed. 

Sample output from the incoming example data: 

floor_result  
---  
3.000000  
  
The result shows that the floor value of `3.7` is `3.000000`, as `3` is the largest integer less than or equal to `3.7`. 

Some other examples demonstrating floor values: 

  * `math:floor(3.0) = 3.000000` (integer input returns the same integer) 

  * `math:floor(3.1) = 3.000000` (rounds down regardless of decimal value) 

  * `math:floor(-3.7) = -4.000000` (negative numbers round down to next lower integer) 

  * `math:floor(0.8) = 0.000000` (decimal numbers between 0 and 1 round down to 0) 




Note that the [`math:floor()`](functions-math-floor.html "math:floor\(\)") function always rounds down, unlike rounding functions that might round up or down based on the decimal portion. This makes it particularly useful when you need consistent downward rounding behavior.
