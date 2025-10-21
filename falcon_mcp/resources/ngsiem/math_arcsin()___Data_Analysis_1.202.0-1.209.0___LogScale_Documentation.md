# math:arcsin() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-arcsin.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)")

Calculates the arc sine of a field; the returned angle is in the range -π/2 through π/2. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-arcsin.html#query-functions-math-arcsin-as)|  string| optional[a] | `_arcsin`|  The name of the output field.   
[_`field`_](functions-math-arcsin.html#query-functions-math-arcsin-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-arcsin.html#query-functions-math-arcsin-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-arcsin.html#query-functions-math-arcsin-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:arcsin("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:arcsin(field="value")
> 
> These examples show basic structure only.

### [`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Arc Sine of Value

**Calculate the arc sine using the[`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)") function **

##### Query

logscale
    
    
    x := 0.5
    | math:arcsin(x, as=angle)

##### Introduction

In this example, the [`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)") function is used to calculate the arc sine of `0.5`, which represents the angle whose sine is `0.5` (30 degrees or π/6 radians). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 0.5

Assigns the value `0.5` to field x. This value represents the sine ratio of an angle, which should result in an angle of π/6 radians (30 degrees). 

  3. logscale
         
         | math:arcsin(x, as=angle)

Calculates the arc sine of the value in field x and returns the result in radians in a field named angle. If the [_`as`_](functions-math-arcsin.html#query-functions-math-arcsin-as) parameter is not specified, the result is returned in a field named _arcsin as default. 

  4. Event Result set.




##### Summary and Results

The query is used to find angles from sine ratios, which is useful in trigonometric calculations and in determining angles when working with perpendicular components of vectors. 

This query is useful, for example, to calculate angles from height-to-hypotenuse ratios, determine elevation angles, or analyze trigonometric relationships. 

Sample output from the incoming example data: 

angle  
---  
0.5235987755982989  
  
The result shows that the arc sine of `0.5` is approximately `0.5236 radians` (π/6 radians or 30 degrees). This means when the sine of an angle is `0.5`, the angle is `30` degrees. 

Note that the [`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)") function only accepts input values between `-1` and `1` (inclusive) and returns values between `-π/2` and `π/2` radians (-90 to 90 degrees). Values outside this range will result in an error. 

The [`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)") function is often used with [`math:rad2deg()`](functions-math-rad2deg.html "math:rad2deg\(\)") when angles need to be displayed in degrees. Consider creating a dashboard comparing different inverse trigonometric functions ([`math:arcsin()`](functions-math-arcsin.html "math:arcsin\(\)"), [`math:arccos()`](functions-math-arccos.html "math:arccos\(\)"), [`math:arctan()`](functions-math-arctan.html "math:arctan\(\)")) to understand their relationships.
