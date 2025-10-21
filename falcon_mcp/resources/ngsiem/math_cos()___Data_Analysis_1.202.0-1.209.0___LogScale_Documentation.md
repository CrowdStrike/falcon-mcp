# math:cos() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-cos.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:cos()`](functions-math-cos.html "math:cos\(\)")

Calculates the cosine of a field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-cos.html#query-functions-math-cos-as)|  string| optional[a] | `_cos`|  The name of the output field.   
[_`field`_](functions-math-cos.html#query-functions-math-cos-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-cos.html#query-functions-math-cos-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-cos.html#query-functions-math-cos-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:cos("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:cos(field="value")
> 
> These examples show basic structure only.

### [`math:cos()`](functions-math-cos.html "math:cos\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Cosine

**Calculate the cosine of a radian value using the[`math:cos()`](functions-math-cos.html "math:cos\(\)") function **

##### Query

logscale
    
    
    x := 1.0472
    | math:cos(x, as=result)

##### Introduction

In this example, the [`math:cos()`](functions-math-cos.html "math:cos\(\)") function is used to calculate the cosine of `π/3` radians (60 degrees), demonstrating a fundamental trigonometric function with a common radian value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 1.0472

Assigns the double-precision floating-point value `1.0472` (π/3 radians) to a field named x. This common radian value corresponds to `60` degrees and will result in a cosine value of `0.5`. 

  3. logscale
         
         | math:cos(x, as=result)

Calculates the cosine of the radian value in field x and returns the result in a new field named result. If the [_`as`_](functions-math-cos.html#query-functions-math-cos-as) parameter is not specified, the result is returned in a field named _cos as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate cosine values from radian inputs, which are essential in various mathematical and physical applications, such as analyzing periodic phenomena, wave patterns, or circular motion. 

This query is useful, for example, to model oscillating systems, analyze wave functions, calculate coordinates on a circle, or process periodic data patterns. 

Sample output from the incoming example data: 

result  
---  
0.5  
  
The result shows that `math:cos(π/3) = 0.5`. Common radian input values and their results include: `math:cos(0) = 1`, `math:cos(π/2) = 0`, `math:cos(π) = -1`, and `math:cos(2π) = 1`, showing the periodic nature of the function. 

Remember that all trigonometric functions in LogScale expect radian inputs. For angle measurements in degrees, if needed, convert them to radians using the [`math:deg2rad()`](functions-math-deg2rad.html "math:deg2rad\(\)") function.
