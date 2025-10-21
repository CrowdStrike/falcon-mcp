# math:cosh() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-cosh.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:cosh()`](functions-math-cosh.html "math:cosh\(\)")

Computes the hyperbolic cosine of a double field. The hyperbolic cosine of x is defined to be `(ex + e-x)/2` where e is Euler's number. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-cosh.html#query-functions-math-cosh-as)|  string| optional[a] | `_cosh`|  The name of the output field.   
[_`field`_](functions-math-cosh.html#query-functions-math-cosh-field)|  string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.  
  
### [`math:cosh()`](functions-math-cosh.html "math:cosh\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Hyperbolic Cosine

**Calculate the hyperbolic cosine of a radian value using the[`math:cosh()`](functions-math-cosh.html "math:cosh\(\)") function **

##### Query

logscale
    
    
    x := 1.0 // 1 radian
    | math:cosh(x, as=result)

##### Introduction

In this example, the [`math:cosh()`](functions-math-cosh.html "math:cosh\(\)") function is used to calculate the hyperbolic cosine of `1.0` radian, demonstrating how hyperbolic functions differ from their trigonometric counterparts while still using radian inputs. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 1.0 // 1 radian

Assigns the double-precision floating-point value `1.0` radian to a field named x. This value demonstrates how hyperbolic cosine produces non-periodic results from radian inputs. 

  3. logscale
         
         | math:cosh(x, as=result)

Calculates the hyperbolic cosine of the radian value in field x and returns the result in a new field named result. If the [_`as`_](functions-math-cosh.html#query-functions-math-cosh-as) parameter is not specified, the result is returned in a field named _cosh as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate hyperbolic cosine values from radian inputs, which are essential in various mathematical and physical applications, particularly those involving exponential growth patterns. 

This query is useful, for example, to model natural phenomena that follow hyperbolic patterns, such as the shape of suspended cables, magnetic field lines, or certain types of mathematical optimization problems. 

Sample output from the incoming example data: 

result  
---  
1.543080634815244  
  
The result shows that `math:cosh(1.0) 蝶 1.543080634815244`. Common radian input values and their results include: `math:cosh(0) = 1`, `math:cosh(-x) = math:cosh(x)`, and `math:cosh(x) > 1` for all `x`, showing the non-periodic, symmetric nature of the function. 

While both trigonometric and hyperbolic functions use radian inputs, hyperbolic functions produce exponential-based results rather than periodic ones. The input value represents a point on the hyperbolic curve rather than an angle measurement.
