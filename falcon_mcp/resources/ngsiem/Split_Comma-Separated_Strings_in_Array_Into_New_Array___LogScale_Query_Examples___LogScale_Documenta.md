# Split Comma-Separated Strings in Array Into New
    Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-append-split.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Split Comma-Separated Strings in Array Into New Array

Split comma-separated strings in array into new flat array and extend with new values using the [`array:append()`](https://library.humio.com/data-analysis/functions-array-append.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    splitString(field=numbers,by=",",as=numbarr)
    | array:append(array="numbarr[]", values=[4])

### Introduction

The [`array:append()`](https://library.humio.com/data-analysis/functions-array-append.html) function can be used to create a new array based on values from another flat array, provided that the input array has continuous, sequential indexes with no missing indexes. 

Example incoming data might look like this: 
    
    
    |-----------------------|
    | numbers   | "1,2,3"   |
    |-----------------------|

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         splitString(field=numbers,by=",",as=numbarr)
         | array:append(array="numbarr[]", values=[4])

Splits the comma-separated strings in the field numbers into a new array named numbarr[], and then extends this array with new values. 

  3. Event Result set.




### Summary and Results

This query is used to create a new flat array based on values from another flat array, 

Sample output from the incoming example data: 

numbarr[0]| numbarr[1]| numbarr[2]| numbarr[3]  
---|---|---|---  
1| 2| 3| 4
