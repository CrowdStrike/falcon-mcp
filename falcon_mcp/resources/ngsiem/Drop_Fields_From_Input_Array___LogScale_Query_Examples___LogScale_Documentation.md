# Drop Fields From Input Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-drop.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Drop Fields From Input Array

Drop fields in an array using the [`array:drop()`](https://library.humio.com/data-analysis/functions-array-drop.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:drop("a[]")

### Introduction

The [`array:drop()`](https://library.humio.com/data-analysis/functions-array-drop.html) function is used to drop all fields from an input array provided that the array has continuous, sequential indexes with no empty indexes and that it starts at [0]. 

In this example, the [`array:drop()`](https://library.humio.com/data-analysis/functions-array-drop.html) function is used to drop all fields of the array a[]. 

Example incoming data might look like this: 

a[0]=Dog  
---  
a[1]=Cat  
a[42]=Horse  
a[0]=Dog  
b[0]=Cat  
c[0]=Horse  
animal=cow  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:drop("a[]")

Takes the name of the array a[] and drops all fields of this array. Array b[] and array c[] will not be dropped in this example. Be aware that if there are empty entries in the array, only the fields from index 0 up to the first empty index will be dropped. 

  3. Event Result set.




### Summary and Results

The query is used to drop all fields from a specific input array. 

Sample output from the incoming example data: 

b[0]| c[0]| animal  
---|---|---  
Cat| Horse| cow
