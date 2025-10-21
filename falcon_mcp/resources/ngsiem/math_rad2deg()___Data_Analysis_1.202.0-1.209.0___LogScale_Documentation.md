# math:rad2deg() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-rad2deg.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:rad2deg()`](functions-math-rad2deg.html "math:rad2deg\(\)")

Converts angles from radians to degrees. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-rad2deg.html#query-functions-math-rad2deg-as)|  string| optional[a] | `_rad2deg`|  The name of the output field.   
[_`field`_](functions-math-rad2deg.html#query-functions-math-rad2deg-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-rad2deg.html#query-functions-math-rad2deg-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-rad2deg.html#query-functions-math-rad2deg-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:rad2deg("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:rad2deg(field="value")
> 
> These examples show basic structure only.

### [`math:rad2deg()`](functions-math-rad2deg.html "math:rad2deg\(\)") Examples

Click + next to an example below to get the full details.

#### Convert Radians to Degrees

**Convert angles from radians to degrees using the[`math:rad2deg()`](functions-math-rad2deg.html "math:rad2deg\(\)") function **

##### Query

logscale
    
    
    myvalue := 3.14159
    | math:rad2deg(myvalue, as=degrees)

##### Introduction

Common radian to degree conversions: 

  * π radians = 180 degrees 

  * π/2 radians = 90 degrees 

  * π/4 radians = 45 degrees 

  * π/6 radians = 30 degrees 




In this example, the [`math:rad2deg()`](functions-math-rad2deg.html "math:rad2deg\(\)") function is used to convert the radian value `3.14159` to degrees. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         myvalue := 3.14159

Assigns approximately `π` radians to a field named myvalue. This value should convert to approximately `180` degrees. 

  3. logscale
         
         | math:rad2deg(myvalue, as=degrees)

Converts the radian value in the myvalue field to degrees and returns the result in a field named degrees. 

  4. Event Result set.




##### Summary and Results

The query converts an angle measurement from radians to degrees. This conversion is essential when working with trigonometric functions, as many mathematical operations use radians while human-readable angles are typically expressed in degrees. 

This query is useful for converting angular measurements, working with geometric calculations, or transforming mathematical results into more readable formats. The conversion factor used is `180/π` (approximately 57.2958 degrees per radian). 

Sample output from the incoming example data: 

degrees  
---  
180.000  
  
The result shows that `π` radians (approximately `3.14159`) converts to `180` degrees, demonstrating the standard conversion between radians and degrees.
