# math:arctan() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-arctan.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:arctan()`](functions-math-arctan.html "math:arctan\(\)")

Calculates the arc tangent of a value; the returned angle is in the range -π/2 through π/2. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-arctan.html#query-functions-math-arctan-as)|  string| optional[a] | `_arctan`|  The name of the output field.   
[_`field`_](functions-math-arctan.html#query-functions-math-arctan-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-arctan.html#query-functions-math-arctan-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-arctan.html#query-functions-math-arctan-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:arctan("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:arctan(field="value")
> 
> These examples show basic structure only.

### [`math:arctan()`](functions-math-arctan.html "math:arctan\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Arc Tangent of Value

**Calculate the arc tangent using the[`math:arctan()`](functions-math-arctan.html "math:arctan\(\)") function **

##### Query

logscale
    
    
    x := 1.0
    | math:arctan(x, as=angle)

##### Introduction

In this example, the [`math:arctan()`](functions-math-arctan.html "math:arctan\(\)") function is used to calculate the arc tangent of 1.0, which represents a slope of 1 (45-degree angle). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 1.0

Assigns the value `1.0` to field x. This value represents a slope of 1 (rise over run), which should result in an angle of `π/4` radians (45 degrees). 

  3. logscale
         
         | math:arctan(x, as=angle)

Calculates the arc tangent of the value in field x and returns the result in radians in a field named angle. If the [_`as`_](functions-math-arctan.html#query-functions-math-arctan-as) parameter is not specified, the result is returned in a field named _arctan as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate angles from slope values, which is useful in various mathematical and geometric calculations where you need to find an angle from a ratio. 

This query is useful, for example, to calculate angles from slopes, determine inclination from gradients, or analyze ratios in trigonometric calculations. 

Sample output from the incoming example data: 

angle  
---  
0.7853981633974483  
  
The result shows that the arc tangent of `1.0` is approximately `0.7854` radians (π/4 radians or 45 degrees). This means a slope of 1 corresponds to a 45-degree angle. 

Note that the [`math:arctan()`](functions-math-arctan.html "math:arctan\(\)") function only returns values between `-π/2` and `π/2` radians (-90 to 90 degrees). For full angle determination in all directions (0 to 360 degrees), use [`math:arctan2()`](functions-math-arctan2.html "math:arctan2\(\)") instead. 

The [`math:arctan()`](functions-math-arctan.html "math:arctan\(\)") function is often used with [`math:rad2deg()`](functions-math-rad2deg.html "math:rad2deg\(\)") when angles need to be displayed in degrees. For applications requiring angles in all directions, consider using [`math:arctan2()`](functions-math-arctan2.html "math:arctan2\(\)") instead.
