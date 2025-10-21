# Check For Existence of Element Contained in Given List of Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-arrayexists-in-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check For Existence of Element Contained in Given List of Values

Check for the existence of an element contained in a given list of simple values in a flat array using [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function with in() 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvparse()
    | array:exists(array="a[]", condition=in(a, values=[3, 4]))

### Introduction

The [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function can be used to check for the existence of an element satisfying a condition expressed as a pipeline, but it also allows the direct use of other filter functions. 

In this example, the [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function is used with the _`condition`_ argument and the filter function [`in()`](https://library.humio.com/data-analysis/functions-in.html) to check if given values are in the array. 

Example incoming data might look like this: 

a[0]| a[1]  
---|---  
1| 2  
1| 3  
1| 4  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         kvparse()

Parses the string into key value pairs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | array:exists(array="a[]", condition=in(a, values=[3, 4]))

Filters for events where the a[] array contains the values `3` or `4`. 

  4. Event Result set.




### Summary and Results

The query is used to check for the existence of simple values in a flat array. 

Sample output from the incoming example data: 
    
    
    "a[0]","a[1]"
    "1","3"
    "1","4"
