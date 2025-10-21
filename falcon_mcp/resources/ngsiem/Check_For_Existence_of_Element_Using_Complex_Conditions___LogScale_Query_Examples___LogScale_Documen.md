# Check For Existence of Element Using Complex Conditions | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-arrayexists-in-if-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check For Existence of Element Using Complex Conditions

Check for the existence of elements using complex conditions in flat array using [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function with [`in()`](https://library.humio.com/data-analysis/functions-in.html) and [`if()`](https://library.humio.com/data-analysis/functions-if.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvParse()
    | array:exists(
    array="a[]",
    condition=if(in(a, values=[2,5]), then=true, else=in(a, values=[3, 6]))

### Introduction

The [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function can be used to check for the existence of an element satisfying a condition expressed as a pipeline, but it also allows the direct use of other filter functions. 

In this example, the [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function is used with the _`condition`_ argument and [`if()`](https://library.humio.com/data-analysis/functions-if.html) function along with the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function to check if given values are in the array. 

The example demonstrates how to use the [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) function along with the [`if()`](https://library.humio.com/data-analysis/functions-if.html) function to create a logical OR-like condition in the expression language. It allows for more complex filtering logic, when a direct logical `OR` operator is not available. 

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
         
         kvParse()

Parses the string into key value pairs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | array:exists(
         array="a[]",
         condition=if(in(a, values=[2,5]), then=true, else=in(a, values=[3, 6]))

Filters for events where the a[] array contains the values `2` or `5`. If not containing these values, it filters for events where the a[] array contains the values `3` or `6`. 

  4. Event Result set.




### Summary and Results

The query is used to check for the existence of simple values in nested arrays. 

Sample output from the incoming example data: 

a[0]| a[1]  
---|---  
1| 2  
1| 3
