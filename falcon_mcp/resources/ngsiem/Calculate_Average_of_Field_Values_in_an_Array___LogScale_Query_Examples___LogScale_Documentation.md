# Calculate Average of Field Values in an Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-reducerow.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Average of Field Values in an Array

Calculate Average of Field Values in a flat array using the [`array:reduceRow()`](https://library.humio.com/data-analysis/functions-array-reducerow.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:reduceRow("ages[]", var=x, function=avg(x))

### Introduction

The [`array:reduceRow()`](https://library.humio.com/data-analysis/functions-array-reducerow.html) function can be used together with the aggregate function [`avg()`](https://library.humio.com/data-analysis/functions-avg.html) as the function argument to calculate the average of field values in a flat array. 

In this example, the [`array:reduceRow()`](https://library.humio.com/data-analysis/functions-array-reducerow.html) function is used to calculate the average age of the field ages and return the result in a field named _reduceRow._avg. 

Example incoming data might look like this: 

ages[0]| ages[1]| ages[2]  
---|---|---  
16| 32| 64  
15| 30| 45  
1| 2| 4  
89| 57| 67  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:reduceRow("ages[]", var=x, function=avg(x))

Produces two events, calculating the average value across the ages[] array for each event. The results are placed into the _avg field for each new event. 

  3. Event Result set.




### Summary and Results

The query is used to calculate averages for a given array for each event and is a shorthand version of using [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) specifically for processing each event. 

Sample output from the incoming example data: 

ages[0]| ages[1]| ages[2]| _avg  
---|---|---|---  
16| 32| 64| 37.333  
15| 30| 45| 30  
1| 2| 4| 2.67  
89| 57| 67| 71  
  
Note that the evaluation is per event, for example per row of the overall table of values across the array over all events. To calculate values across the column of values, use [`array:reduceColumn()`](https://library.humio.com/data-analysis/functions-array-reducecolumn.html).
