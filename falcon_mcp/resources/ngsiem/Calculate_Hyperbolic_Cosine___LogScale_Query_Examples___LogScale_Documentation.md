# Calculate Hyperbolic Cosine | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathcosh-hyperbolic-cosine.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Hyperbolic Cosine

Calculate the hyperbolic cosine of a radian value using the [`math:cosh()`](https://library.humio.com/data-analysis/functions-math-cosh.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 1.0 // 1 radian
    | math:cosh(x, as=result)

### Introduction

The [`math:cosh()`](https://library.humio.com/data-analysis/functions-math-cosh.html) function can be used to calculate the hyperbolic cosine of a double-precision value in radians. The hyperbolic cosine is defined as (`e^x + e^-x)/2`, where `e` is Euler's number. Like all hyperbolic functions, it operates on radian inputs but produces non-periodic, exponential-based results. 

In this example, the [`math:cosh()`](https://library.humio.com/data-analysis/functions-math-cosh.html) function is used to calculate the hyperbolic cosine of `1.0` radian, demonstrating how hyperbolic functions differ from their trigonometric counterparts while still using radian inputs. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 1.0 // 1 radian

Assigns the double-precision floating-point value `1.0` radian to a field named x. This value demonstrates how hyperbolic cosine produces non-periodic results from radian inputs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:cosh(x, as=result)

Calculates the hyperbolic cosine of the radian value in field x and returns the result in a new field named result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-cosh.html#query-functions-math-cosh-as) parameter is not specified, the result is returned in a field named _cosh as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate hyperbolic cosine values from radian inputs, which are essential in various mathematical and physical applications, particularly those involving exponential growth patterns. 

This query is useful, for example, to model natural phenomena that follow hyperbolic patterns, such as the shape of suspended cables, magnetic field lines, or certain types of mathematical optimization problems. 

Sample output from the incoming example data: 

result  
---  
1.543080634815244  
  
The result shows that `math:cosh(1.0) 蝶 1.543080634815244`. Common radian input values and their results include: `math:cosh(0) = 1`, `math:cosh(-x) = math:cosh(x)`, and `math:cosh(x) > 1` for all `x`, showing the non-periodic, symmetric nature of the function. 

While both trigonometric and hyperbolic functions use radian inputs, hyperbolic functions produce exponential-based results rather than periodic ones. The input value represents a point on the hyperbolic curve rather than an angle measurement.
