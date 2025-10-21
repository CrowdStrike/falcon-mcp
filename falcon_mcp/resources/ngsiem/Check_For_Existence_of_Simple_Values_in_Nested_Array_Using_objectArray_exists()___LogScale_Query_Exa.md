# Check For Existence of Simple Values in Nested Array Using objectArray:exists()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarrayexists-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check For Existence of Simple Values in Nested Array Using [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html)

Check for the existence of simple values in nested array using [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html) function with [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) as filter function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvParse()
    | objectArray:exists(
    array="a[]",
    condition=array:exists(array="a.field.b[]", var=x, condition=test(x==2)))

### Introduction

The [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html) function can be used to check for the existence of an element satisfying a condition expressed as a pipeline in nested array. 

In this example, the [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html) function is used with the _`condition`_ argument and [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function to check if given values are in the array. 

The `objectArray:exist()` part handles the structured part of the example, whereas the [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) is used within the condition to loop through the nested array. In a nested array, the outermost call must be [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html), the inner one could in theory be either function, but LogScale recommends using [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html). 

Example incoming data might look like this: 

a[0].field.b[0]| a[0].field.b[1]| a[1].field.b[0]| a[2].field.b[0]  
---|---|---|---  
1| <no value>| <no value>| <no value>  
1| 2| <no value>| <no value>  
<no value>| <no value>| 3| <no value>  
1| 2| 3| 4  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | objectArray:exists(
         array="a[]",
         condition=array:exists(array="a.field.b[]", var=x, condition=test(x==2)))

Filters for elements in the array a[] that meet the given condition, then checks if there exists a value in the a.field.b[] array that equals `2`. 

  4. Event Result set.




### Summary and Results

The query is used to test for the existence of simple values in nested arrays. The query outputs the events that passed the filtering condition. 

Sample output from the incoming example data: 

a[0].field.b[0]| a[0].field.b[1]| a[1].field.b[0]| a[2].field.b[0]  
---|---|---|---  
1| 2| <no value>| <no value>  
1| 2| 3| 4
