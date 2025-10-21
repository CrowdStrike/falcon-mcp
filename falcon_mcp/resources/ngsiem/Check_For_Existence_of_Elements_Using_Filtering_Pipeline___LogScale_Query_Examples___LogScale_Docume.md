# Check For Existence of Elements Using Filtering Pipeline | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-arrayexists-filtering-pipeline.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check For Existence of Elements Using Filtering Pipeline

Check for the existence of element in a flat array using the [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function with a filtering pipeline 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvParse()
    | array:exists(
    array="a[]",
    var=x,
    condition={ x=3 OR x=4 | test(x>=b) })

### Introduction

The [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function can be used to check for the existence of an element satisfying a condition expressed as a pipeline. 

In this example, the [`array:exists()`](https://library.humio.com/data-analysis/functions-array-exists.html) function is used with the _`condition`_ argument and [`test()`](https://library.humio.com/data-analysis/functions-test.html) function to check if given values are in the array. 

Example incoming data might look like this: 

a[0]| a[1]| b  
---|---|---  
1| 2| 4  
1| 3| 4  
1| 4| 3  
  
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
         var=x,
         condition={ x=3 OR x=4 | test(x>=b) })

Filters for events where the a[] array contains the values `3` or `4` and where x is greater than or equal to the value of the field b in the event. 

  4. Event Result set.




### Summary and Results

The query is used to compare array entries to both fixed values and field values. The query outputs the event that passed the filtering condition in the pipeline. 

Sample output from the incoming example data: 

a[0]| a[1]| b  
---|---|---  
1| 4| 3
