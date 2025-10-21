# Evaluate Function Argument on Values in Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-evaluate-argument.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Evaluate Function Argument on Values in Array

Evaluate the [_`function`_](https://library.humio.com/data-analysis/functions-array-eval.html#query-functions-array-eval-function) argument on all values in a flat array 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Update Field Data\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00;

logscale
    
    
    array:eval("values[]", asArray="squared[]", var="x", function={squared := x*x})

### Introduction

The [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function is used for test purposes. It evaluates the [_`function`_](https://library.humio.com/data-analysis/functions-array-eval.html#query-functions-array-eval-function) argument on all values in the array under the [_`array`_](https://library.humio.com/data-analysis/functions-array-eval.html#query-functions-array-eval-array) argument overwriting the input array. If an [_`as`_](https://library.humio.com/data-analysis/syntax-fields.html#syntax-fields-from-functions) argument has been supplied, [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) will save the result in an array under the supplied prefix. The purpose of this query is to square the value of each item in the array. 

Example incoming data might look like this: 

values[0]| values[1]| values[2]  
---|---|---  
2| 3| 4  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Update Field Data\\] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:eval("values[]", asArray="squared[]", var="x", function={squared := x*x})

Squares the value of each item in the array. If input values `(x)` are 2,3,4 then the output values when squared `(x*x)` will be 4,9,16. 

  3. Event Result set.




### Summary and Results

The query is used to square the value of each item in the array. This is a good example of manipulating array values, for example to format the output before display. 

Sample output from the incoming example data: 

field| value  
---|---  
squared[0]| 4  
squared[1]| 9  
squared[2]| 16
