# Calculate Arc Cosine of Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-matharccos-calculate-arccosine.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Arc Cosine of Value

Calculate the arc cosine using the [`math:arccos()`](https://library.humio.com/data-analysis/functions-math-arccos.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 0.5
    | math:arccos(x, as=angle)

### Introduction

The [`math:arccos()`](https://library.humio.com/data-analysis/functions-math-arccos.html) function can be used to calculate the inverse cosine (arc cosine) of a value, returning the angle in radians. The function accepts values between `-1` and `1`, and returns an angle in the range `0` to `π` radians (from 0 to 180 degrees). 

In this example, the [`math:arccos()`](https://library.humio.com/data-analysis/functions-math-arccos.html) function is used to calculate the arc cosine of `0.5`, which represents the angle whose cosine is `0.5` (60 degrees or π/3 radians). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 0.5

Assigns the value `0.5` to field x. This value represents the cosine ratio of an angle, which should result in an angle of π/3 radians (60 degrees). 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:arccos(x, as=angle)

Calculates the arc cosine of the value in field x and returns the result in radians in a field named angle. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-arccos.html#query-functions-math-arccos-as) parameter is not specified, the result is returned in a field named _arccos as default. 

  4. Event Result set.




### Summary and Results

The query is used to find angles from cosine ratios, which is useful in trigonometric calculations and in determining angles when working with adjacent components of vectors. 

This query is useful, for example, to calculate angles from adjacent-to-hypotenuse ratios, determine angles in geometric problems, or analyze trigonometric relationships. 

Sample output from the incoming example data: 

angle  
---  
1.0471975511965979  
  
The result shows that the arc cosine of `0.5` is approximately `1.0472 radians` (π/3 radians or 60 degrees). This means when the cosine of an angle is `0.5`, the angle is `60` degrees. 

Note that the [`math:arccos()`](https://library.humio.com/data-analysis/functions-math-arccos.html) function only accepts input values between `-1` and `1` (inclusive) and returns values between `0` and `π` radians (0 to 180 degrees). Values outside this range will result in an error. 

The [`math:arccos()`](https://library.humio.com/data-analysis/functions-math-arccos.html) function is often used with [`math:rad2deg()`](https://library.humio.com/data-analysis/functions-math-rad2deg.html) when angles need to be displayed in degrees. Consider creating a dashboard comparing different inverse trigonometric functions ([`math:arcsin()`](https://library.humio.com/data-analysis/functions-math-arcsin.html), [`math:arccos()`](https://library.humio.com/data-analysis/functions-math-arccos.html), [`math:arctan()`](https://library.humio.com/data-analysis/functions-math-arctan.html)) to understand their relationships.
