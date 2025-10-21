# Calculate Hyperbolic Tangent Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathtanh-calculate-single-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Hyperbolic Tangent Values

Calculate hyperbolic tangent using the [`math:tanh()`](https://library.humio.com/data-analysis/functions-math-tanh.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    myvalue := 120
    | math:tanh(myvalue, as=tanh_value)

### Introduction

The [`math:tanh()`](https://library.humio.com/data-analysis/functions-math-tanh.html) function calculates the hyperbolic tangent of a value. The hyperbolic tangent is the ratio of sinh to cosh and always returns values between `-1` and `1`. 

In this example, the [`math:tanh()`](https://library.humio.com/data-analysis/functions-math-tanh.html) function is used to calculate the hyperbolic tangent of an assigned value of `120`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         myvalue := 120

Assigns the value `120` to a field named myvalue. This creates a new field with a constant value that will be used for the hyperbolic tangent calculation. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:tanh(myvalue, as=tanh_value)

Calculates the hyperbolic tangent of the value in the myvalue field and returns the result in a new field named tanh_value. The result will be between `-1` and `1`, with larger input values producing results closer to `-1` or `1`. 

Since `120` is a large positive number, the result will be very close to `1` due to the asymptotic nature of the hyperbolic tangent function. 

Mathematically, `tanh(x) = sinh(x)/cosh(x) = (eˣ - e⁻ˣ)/(eˣ + e⁻ˣ)`, where `e` is Euler's number. 

  4. Event Result set.




### Summary and Results

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
