# Square Values in an Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-eval.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Square Values in an Array

Square values in an array using the [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:eval("values[]", asArray="squared[]", var=element, function={squared :=element*element})

### Introduction

The [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function is used to apply a specific function to each value inside an array. The [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function processes every item in the list (array) one by one, performs some kind of calculation or operation, and either overwrites the original array or saves the result in a new array. 

In this example, the [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function is used to square a list of numbers (for example `2`, `3`, and `4`) and show the results in a new array. 

Example incoming data might look like this: 

values [0] = 2  
---  
values [1] = 3  
values [2] = 4  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:eval("values[]", asArray="squared[]", var=element, function={squared :=element*element})

Squares all values in the array values[] and returns the results in a new array named squared[]. The values in the original array stay the same: `[2, 3, 4]` and the new array contains the squared results: `[4, 9, 16]`

  3. Event Result set.




### Summary and Results

The query is used to square a list of numbers in an array. The [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function can also be used for performing formatting on values in an array. 

Sample output from the incoming example data: 

field| value  
---|---  
squared[0]| 4  
squared[1]| 9  
squared[2]| 16
