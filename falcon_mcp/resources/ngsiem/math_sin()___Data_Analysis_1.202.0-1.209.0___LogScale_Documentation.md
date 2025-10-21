# math:sin() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-sin.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:sin()`](functions-math-sin.html "math:sin\(\)")

Calculates the sine of a field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-sin.html#query-functions-math-sin-as)|  string| optional[a] | `_sin`|  The name of the output field.   
[_`field`_](functions-math-sin.html#query-functions-math-sin-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-sin.html#query-functions-math-sin-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-sin.html#query-functions-math-sin-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:sin("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:sin(field="value")
> 
> These examples show basic structure only.

### [`math:sin()`](functions-math-sin.html "math:sin\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Sine of a Value

**Compute trigonometric sine using the[`math:sin()`](functions-math-sin.html "math:sin\(\)") function **

##### Query

logscale
    
    
    myvalue := 345
    | math:sin(myvalue, as=mathvalue)

##### Introduction

In this example, the [`math:sin()`](functions-math-sin.html "math:sin\(\)") function is used to calculate the sine of a positive value, demonstrating how the function handles standard input. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         myvalue := 345

Assigns the positive value `345` to a variable named myvalue for use in subsequent calculations. 

  3. logscale
         
         | math:sin(myvalue, as=mathvalue)

Calculates the sine of the value in the myvalue field and returns the result in a new field named mathvalue. The [`math:sin()`](functions-math-sin.html "math:sin\(\)") function automatically handles the conversion of the input value to radians and returns a value between -1 and 1. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate the sine of a positive angle value, demonstrating basic trigonometric calculations. 

This query is useful, for example, to analyze periodic data, process angular measurements, or calculate wave functions in scientific applications. 

Sample output from the incoming example data: 

mathvalue  
---  
-0.9589243  
  
Note that the sine value for 345 radians is the exact opposite of the sine of -345 radians, demonstrating the odd symmetry property of the sine function where `sin(-x) = -sin(x)`.
