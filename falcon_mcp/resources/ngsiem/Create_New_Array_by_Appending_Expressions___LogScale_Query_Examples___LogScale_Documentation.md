# Create New Array by Appending Expressions | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-append-newarray.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create New Array by Appending Expressions

Create a new flat array by appending new expressions using the [`array:append()`](https://library.humio.com/data-analysis/functions-array-append.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:append(array="related.user[]", values=[lower(source.user.name), lower(destination.user.name)])

### Introduction

The [`array:append()`](https://library.humio.com/data-analysis/functions-array-append.html) function can be used to create a new array based on values from an array of expressions, provided that the input array has continuous, sequential indexes with no missing indexes. 

In this example, the [`array:append()`](https://library.humio.com/data-analysis/functions-array-append.html) function is used to create a new array related.user[] containing information about all user names seen on the event. 

Example incoming data might look like this: 
    
    
    source.user.name="user_1" destination.user.name="USER_2"

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:append(array="related.user[]", values=[lower(source.user.name), lower(destination.user.name)])

Creates a new array related.user[] containing information about all user names seen on the event. Notice that the [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) function formats the results into lower case before appending them to the array. 

  3. Event Result set.




### Summary and Results

This query is used to create a new flat array based on values from an array of expressions. 

Sample output from the incoming example data: 

source.user.name| destination.user.name| related.user[0]| related.user[1]|   
---|---|---|---|---  
user_1| USER_2| user_1| user_2|
