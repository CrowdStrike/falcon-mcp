# Subtract Values From Two Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-subtract-field-values.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Subtract Values From Two Fields

Calculate the difference of values from two fields using the subtraction operator (`-`) 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    result:=a-b

### Introduction

Mathematical operations can be performed on field values to calculate new results. Multiplication, addition, subtraction and division do not require usage of a function. 

In this example, subtraction is used to calculate the difference of values from fields a and b, storing the result in a new field. 

Example incoming data might look like this: 

@timestamp| a| b  
---|---|---  
2025-09-15T10:00:00Z| 10| 4  
2025-09-15T10:00:01Z| 15| 3  
2025-09-15T10:00:02Z| 20| 8  
2025-09-15T10:00:03Z| 12| 6  
2025-09-15T10:00:04Z| 18| 5  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         result:=a-b

Subtracts the value in field b from the value in field a and assigns the result to a new field named result. The subtraction operator (`-`) performs the calculation on the numerical values from both fields. 

  3. Event Result set.




### Summary and Results

The query is used to subtract values from two different fields and store the result in a new field. 

This query is useful, for example, to calculate profit margins (revenue \- costs), remaining inventory (initial_stock - sold_items), or any other subtraction-based calculations from field values. 

Sample output from the incoming example data: 

a| b| result  
---|---|---  
10| 4| 6  
15| 3| 12  
20| 8| 12  
12| 6| 6  
18| 5| 13  
  
The results of this subtraction query can be effectively visualized using various widgets. A Time Chart widget could show how the difference values change over time. For comparing the original values with their differences, a Table widget would be most appropriate, allowing side-by-side comparison of the input fields and their calculated results.
