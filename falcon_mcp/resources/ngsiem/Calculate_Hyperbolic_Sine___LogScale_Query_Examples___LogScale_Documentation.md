# Calculate Hyperbolic Sine | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathsinh-hyperbolic.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Hyperbolic Sine

Compute hyperbolic sine values using the [`math:sinh()`](https://library.humio.com/data-analysis/functions-math-sinh.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    myvalue := 2.5
    | math:sinh(myvalue, as=hyperbolic_sine)

### Introduction

The [`math:sinh()`](https://library.humio.com/data-analysis/functions-math-sinh.html) function can be used to calculate the hyperbolic sine of a value. Unlike the regular sine function, hyperbolic sine can return any real number and is not bounded between -1 and 1. 

In this example, the [`math:sinh()`](https://library.humio.com/data-analysis/functions-math-sinh.html) function is used to calculate the hyperbolic sine of a value, demonstrating how this hyperbolic function differs from regular trigonometric sine. 

Example incoming data might look like this: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         myvalue := 2.5

Assigns the value `2.5` to a variable named myvalue for use in the hyperbolic calculation. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:sinh(myvalue, as=hyperbolic_sine)

Calculates the hyperbolic sine of the value in the myvalue field and returns the result in a new field named hyperbolic_sine. The [`math:sinh()`](https://library.humio.com/data-analysis/functions-math-sinh.html) function computes the value using the formula` (e^x - e^-x)/2`, where `e` is Euler's number. 

  4. Event Result set.




### Summary and Results

The query is used to calculate hyperbolic sine values, which are important in various mathematical and physical applications. 

This query is useful, for example, to analyze exponential growth patterns, solve differential equations, or process data in fields such as electrical engineering and physics where hyperbolic functions are commonly used. 

Sample output from the incoming example data: 

hyperbolic_sine  
---  
6.0502044  
  
Note that the hyperbolic sine function is an odd function, meaning `sinh(-x) = -sinh(x)`.
