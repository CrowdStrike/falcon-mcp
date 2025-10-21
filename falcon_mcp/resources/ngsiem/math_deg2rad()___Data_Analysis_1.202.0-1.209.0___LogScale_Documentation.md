# math:deg2rad() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-deg2rad.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:deg2rad()`](functions-math-deg2rad.html "math:deg2rad\(\)")

Converts angles from degrees to radians. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-deg2rad.html#query-functions-math-deg2rad-as)|  string| optional[a] | `_deg2rad`|  The name of the output field.   
[_`field`_](functions-math-deg2rad.html#query-functions-math-deg2rad-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-deg2rad.html#query-functions-math-deg2rad-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-deg2rad.html#query-functions-math-deg2rad-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:deg2rad("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:deg2rad(field="value")
> 
> These examples show basic structure only.

### [`math:deg2rad()`](functions-math-deg2rad.html "math:deg2rad\(\)") Examples

Click + next to an example below to get the full details.

#### Convert Degrees to Radians

**Convert angles from degrees to radians using the[`math:deg2rad()`](functions-math-deg2rad.html "math:deg2rad\(\)") function **

##### Query

logscale
    
    
    myvalue := 180.0
            | math:deg2rad(myvalue, as=radians)

##### Introduction

Common degree to radian conversions: 

  * 180 degrees = π radians 

  * 90 degrees = π/2 radians 

  * 45 degrees = π/4 radians 

  * 30 degrees = π/6 radians 




In this example, the [`math:deg2rad()`](functions-math-deg2rad.html "math:deg2rad\(\)") function is used to convert the degree value `180` to radians. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         myvalue := 180.0

Assigns `180` degrees to a field named myvalue. This value should convert to approximately `π` radians. 

  3. logscale
         
         | math:deg2rad(myvalue, as=radians)

Converts the degree value in the myvalue field to radians and returns the result in a field named radians. 

  4. Event Result set.




##### Summary and Results

The query converts an angle measurement from degrees to radians. This conversion is essential when working with trigonometric functions, as many mathematical operations require radians rather than degrees. 

This query is useful for preparing angular measurements for mathematical calculations, working with geometric computations, or transforming human-readable angles into formats suitable for mathematical operations. The conversion factor used is `π/180` (approximately 0.0174533 radians per degree). 

Sample output from the incoming example data: 

radians  
---  
3.14159  
  
The result shows that `180` degrees converts to `π` radians (approximately `3.14159`), demonstrating the standard conversion between degrees and radians.
