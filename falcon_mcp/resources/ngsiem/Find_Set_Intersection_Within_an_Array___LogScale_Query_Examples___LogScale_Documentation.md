# Find Set Intersection Within an Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-intersection.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Set Intersection Within an Array

Find set intersection within a single flat array using the [`array:intersection()`](https://library.humio.com/data-analysis/functions-array-intersection.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:intersection("mailto[]", as=unique_mails)

### Introduction

Set intersection refers to finding the common elements within array. The result of the intersection operation is a new dataset containing only the elements that are common to all the input sets (similar to a join operation). 

In this example, the [`array:intersection()`](https://library.humio.com/data-analysis/functions-array-intersection.html) function will return the unique email addresses from an array. The intersection of the array is based on the intersection of unique values within each element. 

Example incoming data might look like this: 

logscale
    
    
    mailto[0]=foo@example.com
    mailto[1]=bar@example.com
    mailto[2]=bar@example.com

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:intersection("mailto[]", as=unique_mails)

Returns the intersection of element values in the array mailto[], in this case email addresses, storing the result in a new intersection set array unique_mails and stores them as unique values. 

  3. Event Result set.




### Summary and Results

The result of the intersection operation is a new dataset that consists of all the common elements occurring in an array. The query is used to simplify data in an array for any common values and make a new array with only the unique values in it. This can be useful when processing a set of values and looking for the unique list, for example to use as labels within a graph, or as input parameters to a filter. 

Sample output from the incoming example data: 

logscale
    
    
    unique_mails[0]=foo@example.com
    unique_mails[1]=bar@example.com
