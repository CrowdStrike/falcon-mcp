# math:abs() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-abs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:abs()`](functions-math-abs.html "math:abs\(\)")

Calculates the absolute value of a field. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-abs.html#query-functions-math-abs-as)|  string| optional[a] | `_abs`|  The name of the output field.   
[_`field`_](functions-math-abs.html#query-functions-math-abs-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-abs.html#query-functions-math-abs-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-abs.html#query-functions-math-abs-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:abs("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:abs(field="value")
> 
> These examples show basic structure only.

### [`math:abs()`](functions-math-abs.html "math:abs\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Absolute Value

**Calculate the absolute value using the[`math:abs()`](functions-math-abs.html "math:abs\(\)") function **

##### Query

logscale
    
    
    x := -3.5
    | math:abs(x, as=result)

##### Introduction

In this example, the [`math:abs()`](functions-math-abs.html "math:abs\(\)") function is used to calculate the absolute value of a negative number, demonstrating how it returns the positive version of that number. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := -3.5

Assigns the negative value `-3.5` to field x. This value will demonstrate how the absolute value function removes the negative sign. 

  3. logscale
         
         | math:abs(x, as=result)

Calculates the absolute value of the number in field x and returns the result in a field named result. If the [_`as`_](functions-math-abs.html#query-functions-math-abs-as) parameter is not specified, the result is returned in a field named _abs as default. 

  4. Event Result set.




##### Summary and Results

The query is used to find the absolute value of a number, which is useful when you need to know the size of a value without considering whether it is positive or negative. 

This query is useful, for example, to calculate distances, determine the size of differences, or measure deviations from a reference point. 

Sample output from the incoming example data: 

result  
---  
3.5  
  
The result shows that the absolute value of `-3.5` is `3.5`, demonstrating how the function removes the negative sign. 

Note that the [`math:abs()`](functions-math-abs.html "math:abs\(\)") function works with both integer and decimal values. For example, `math:abs(-3.5) = 3.5`, `math:abs(3.5) = 3.5`, and `math:abs(0) = 0`. 

The [`math:abs()`](functions-math-abs.html "math:abs\(\)") function is particularly useful in dashboards where you need to analyze values regardless of their sign, such as measuring deviations from a baseline or calculating differences between values.
