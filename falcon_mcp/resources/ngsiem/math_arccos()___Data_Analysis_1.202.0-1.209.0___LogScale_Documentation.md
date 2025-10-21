# math:arccos() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-arccos.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:arccos()`](functions-math-arccos.html "math:arccos\(\)")

Calculates the arc cosine of a field; the returned angle is in the range 0.0 through π. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-arccos.html#query-functions-math-arccos-as)|  string| optional[a] | `_arccos`|  The name of the output field.   
[_`field`_](functions-math-arccos.html#query-functions-math-arccos-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-arccos.html#query-functions-math-arccos-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-arccos.html#query-functions-math-arccos-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:arccos("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:arccos(field="value")
> 
> These examples show basic structure only.

### [`math:arccos()`](functions-math-arccos.html "math:arccos\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Arc Cosine of Value

**Calculate the arc cosine using the[`math:arccos()`](functions-math-arccos.html "math:arccos\(\)") function **

##### Query

logscale
    
    
    x := 0.5
    | math:arccos(x, as=angle)

##### Introduction

In this example, the [`math:arccos()`](functions-math-arccos.html "math:arccos\(\)") function is used to calculate the arc cosine of `0.5`, which represents the angle whose cosine is `0.5` (60 degrees or π/3 radians). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 0.5

Assigns the value `0.5` to field x. This value represents the cosine ratio of an angle, which should result in an angle of π/3 radians (60 degrees). 

  3. logscale
         
         | math:arccos(x, as=angle)

Calculates the arc cosine of the value in field x and returns the result in radians in a field named angle. If the [_`as`_](functions-math-arccos.html#query-functions-math-arccos-as) parameter is not specified, the result is returned in a field named _arccos as default. 

  4. Event Result set.




##### Summary and Results

The query is used to find angles from cosine ratios, which is useful in trigonometric calculations and in determining angles when working with adjacent components of vectors. 

This query is useful, for example, to calculate angles from adjacent-to-hypotenuse ratios, determine angles in geometric problems, or analyze trigonometric relationships. 

Sample output from the incoming example data: 

angle  
---  
1.0471975511965979  
  
The result shows that the arc cosine of `0.5` is approximately `1.0472 radians` (π/3 radians or 60 degrees). This means when the cosine of an angle is `0.5`, the angle is `60` degrees. 

Note that the [`math:arccos()`](functions-math-arccos.html "math:arccos\(\)") function only accepts input values between `-1` and `1` (inclusive) and returns values between `0` and `π` radians (0 to 180 degrees). Values outside this range will result in an error. 

The [`math:arccos()`](functions-math-arccos.html "math:arccos\(\)") function is often used with [`math:rad2deg()`](functions-math-rad2deg.html "math:rad2deg\(\)") when angles need to be displayed in degrees. Consider creating a dashboard comparing different inverse trigonometric functions ([`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)"), [`math:arccos()`](functions-math-arccos.html "math:arccos\(\)"), [`math:arctan()`](functions-math-arctan.html "math:arctan\(\)")) to understand their relationships.
