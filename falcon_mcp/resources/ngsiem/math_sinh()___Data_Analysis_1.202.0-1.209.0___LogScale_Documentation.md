# math:sinh() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-sinh.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:sinh()`](functions-math-sinh.html "math:sinh\(\)")

Calculates the hyperbolic sine of a double field. The hyperbolic sine of x is defined to be `(ex - e-x)/2` where e is Euler's number. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-sinh.html#query-functions-math-sinh-as)|  string| optional[a] | `_sinh`|  The name of the output field.   
[_`field`_](functions-math-sinh.html#query-functions-math-sinh-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-sinh.html#query-functions-math-sinh-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-sinh.html#query-functions-math-sinh-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:sinh("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:sinh(field="value")
> 
> These examples show basic structure only.

### [`math:sinh()`](functions-math-sinh.html "math:sinh\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Hyperbolic Sine

**Compute hyperbolic sine values using the[`math:sinh()`](functions-math-sinh.html "math:sinh\(\)") function **

##### Query

logscale
    
    
    myvalue := 2.5
    | math:sinh(myvalue, as=hyperbolic_sine)

##### Introduction

In this example, the [`math:sinh()`](functions-math-sinh.html "math:sinh\(\)") function is used to calculate the hyperbolic sine of a value, demonstrating how this hyperbolic function differs from regular trigonometric sine. 

Example incoming data might look like this: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         myvalue := 2.5

Assigns the value `2.5` to a variable named myvalue for use in the hyperbolic calculation. 

  3. logscale
         
         | math:sinh(myvalue, as=hyperbolic_sine)

Calculates the hyperbolic sine of the value in the myvalue field and returns the result in a new field named hyperbolic_sine. The [`math:sinh()`](functions-math-sinh.html "math:sinh\(\)") function computes the value using the formula` (e^x - e^-x)/2`, where `e` is Euler's number. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate hyperbolic sine values, which are important in various mathematical and physical applications. 

This query is useful, for example, to analyze exponential growth patterns, solve differential equations, or process data in fields such as electrical engineering and physics where hyperbolic functions are commonly used. 

Sample output from the incoming example data: 

hyperbolic_sine  
---  
6.0502044  
  
Note that the hyperbolic sine function is an odd function, meaning `sinh(-x) = -sinh(x)`.
