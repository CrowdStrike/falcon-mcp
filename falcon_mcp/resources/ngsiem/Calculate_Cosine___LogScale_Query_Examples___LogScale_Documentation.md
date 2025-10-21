# Calculate Cosine | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathcos-cosine.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Cosine

Calculate the cosine of a radian value using the [`math:cos()`](https://library.humio.com/data-analysis/functions-math-cos.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 1.0472
    | math:cos(x, as=result)

### Introduction

The [`math:cos()`](https://library.humio.com/data-analysis/functions-math-cos.html) function can be used to calculate the cosine of a double-precision value in radians. The cosine function is a periodic function that oscillates between `-1` and `1`, completing one full cycle every `2π` radians (360 degrees). 

The input angle is provided in radians. If needed, [`math:deg2rad()`](https://library.humio.com/data-analysis/functions-math-deg2rad.html) converts from degrees to radians. 

In this example, the [`math:cos()`](https://library.humio.com/data-analysis/functions-math-cos.html) function is used to calculate the cosine of `π/3` radians (60 degrees), demonstrating a fundamental trigonometric function with a common radian value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 1.0472

Assigns the double-precision floating-point value `1.0472` (π/3 radians) to a field named x. This common radian value corresponds to `60` degrees and will result in a cosine value of `0.5`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:cos(x, as=result)

Calculates the cosine of the radian value in field x and returns the result in a new field named result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-cos.html#query-functions-math-cos-as) parameter is not specified, the result is returned in a field named _cos as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate cosine values from radian inputs, which are essential in various mathematical and physical applications, such as analyzing periodic phenomena, wave patterns, or circular motion. 

This query is useful, for example, to model oscillating systems, analyze wave functions, calculate coordinates on a circle, or process periodic data patterns. 

Sample output from the incoming example data: 

result  
---  
0.5  
  
The result shows that `math:cos(π/3) = 0.5`. Common radian input values and their results include: `math:cos(0) = 1`, `math:cos(π/2) = 0`, `math:cos(π) = -1`, and `math:cos(2π) = 1`, showing the periodic nature of the function. 

Remember that all trigonometric functions in LogScale expect radian inputs. For angle measurements in degrees, if needed, convert them to radians using the [`math:deg2rad()`](https://library.humio.com/data-analysis/functions-math-deg2rad.html) function.
