# math:tanh() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-tanh.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:tanh()`](functions-math-tanh.html "math:tanh\(\)")

Calculates the hyperbolic tangent of a field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-tanh.html#query-functions-math-tanh-as)|  string| optional[a] | `_tanh`|  The name of the output field.   
[_`field`_](functions-math-tanh.html#query-functions-math-tanh-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-tanh.html#query-functions-math-tanh-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-tanh.html#query-functions-math-tanh-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:tanh("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:tanh(field="value")
> 
> These examples show basic structure only.

### [`math:tanh()`](functions-math-tanh.html "math:tanh\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Hyperbolic Tangent Values

**Calculate hyperbolic tangent using the[`math:tanh()`](functions-math-tanh.html "math:tanh\(\)") function **

##### Query

logscale
    
    
    myvalue := 120
    | math:tanh(myvalue, as=tanh_value)

##### Introduction

In this example, the [`math:tanh()`](functions-math-tanh.html "math:tanh\(\)") function is used to calculate the hyperbolic tangent of an assigned value of `120`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         myvalue := 120

Assigns the value `120` to a field named myvalue. This creates a new field with a constant value that will be used for the hyperbolic tangent calculation. 

  3. logscale
         
         | math:tanh(myvalue, as=tanh_value)

Calculates the hyperbolic tangent of the value in the myvalue field and returns the result in a new field named tanh_value. The result will be between `-1` and `1`, with larger input values producing results closer to `-1` or `1`. 

Since `120` is a large positive number, the result will be very close to `1` due to the asymptotic nature of the hyperbolic tangent function. 

Mathematically, `tanh(x) = sinh(x)/cosh(x) = (eˣ - e⁻ˣ)/(eˣ + e⁻ˣ)`, where `e` is Euler's number. 

  4. Event Result set.




##### Summary and Results

The query calculates the hyperbolic tangent of a fixed value of `120`. Unlike regular tangent, hyperbolic tangent is not periodic and approaches `-1` or `1` asymptotically as the input increases or decreases. 

This query is useful for neural network activation functions, signal processing, data normalization, machine learning applications, and control systems. 

Sample output from the incoming example data: 

tanh_value  
---  
1.000  
  
The result is `1.000` because the input value (120) is large enough that `tanh(120)` is effectively at its asymptotic limit of `1`. 

Note that any input value above approximately `5` will result in a value greater than `0.999`, demonstrating how quickly the hyperbolic tangent function approaches its asymptotic limits. 

If, for example, the calculation had been performed on the input values `4`, `-1` and `5`, then these values are in the range where the hyperbolic tangent function shows its characteristic S-shaped curve behavior, before approaching its asymptotic limit. Sample output would be: 

tanh_value1| tanh_value2| tanh_value3  
---|---|---  
0.999| -0.762| 1.000
