# math:tan() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-tan.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:tan()`](functions-math-tan.html "math:tan\(\)")

Calculates the trigonometric tangent of an angle in a field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-tan.html#query-functions-math-tan-as)|  string| optional[a] | `_tan`|  The name of the output field.   
[_`field`_](functions-math-tan.html#query-functions-math-tan-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-tan.html#query-functions-math-tan-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-tan.html#query-functions-math-tan-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:tan("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:tan(field="value")
> 
> These examples show basic structure only.

### [`math:tan()`](functions-math-tan.html "math:tan\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Tangent Values

**Calculate tangent of angles in radians using the[`math:tan()`](functions-math-tan.html "math:tan\(\)") function **

##### Query

logscale
    
    
    myvalue := 120
    | math:tan(myvalue, as=tangent_value)

##### Introduction

In this example, the [`math:tan()`](functions-math-tan.html "math:tan\(\)") function is used to calculate the tangent of an assigned value of `120` (interpreted as radians). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         myvalue := 120

Assigns the value `120` to a field named myvalue. This creates a new field with a constant value that will be used for the tangent calculation. 

  3. logscale
         
         | math:tan(myvalue, as=tangent_value)

Calculates the tangent of the value in the myvalue field and returns the result in a new field named tangent_value. Note that the input value is interpreted as radians, not degrees. 

  4. Event Result set.




##### Summary and Results

The query calculates the tangent of a fixed value of `120 radians`. Since tangent is a periodic function with period π (approximately 3.14159), the result represents the equivalent angle within one period. 

This query is useful for performing consistent trigonometric calculations across events, testing specific angle values in radians, or adding reference trigonometric values to existing data. 

Sample output from the incoming example data: 

tangent_value  
---  
0.320
