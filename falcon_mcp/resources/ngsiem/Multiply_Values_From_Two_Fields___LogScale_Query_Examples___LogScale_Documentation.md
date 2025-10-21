# Multiply Values From Two Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-multiply-field-values.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Multiply Values From Two Fields

Calculate the product of values from two fields using the multiplication operator (`*`) 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    result:=a*b

### Introduction

Mathematical operations can be performed on field values to calculate new results. Multiplication, addition, subtraction and division do not require usage of a function. 

In this example, multiplication is used to calculate the product of values from fields a and b, storing the result in a new field. 

Example incoming data might look like this: 

@timestamp| a| b  
---|---|---  
2025-09-15T10:00:00Z| 2| 4  
2025-09-15T10:00:01Z| 5| 3  
2025-09-15T10:00:02Z| 10| 2  
2025-09-15T10:00:03Z| 3| 6  
2025-09-15T10:00:04Z| 8| 5  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         result:=a*b

Multiplies the values in fields a and b and assigns the result to a new field named result. The multiplication operator (`*`) performs the calculation on the numerical values from both fields. 

  3. Event Result set.




### Summary and Results

The query is used to multiply values from two different fields and store the result in a new field. 

This query is useful, for example, to calculate total areas (length × width), total costs (quantity × price), or any other multiplication-based calculations from field values. 

Sample output from the incoming example data: 

a| b| result  
---|---|---  
2| 4| 8  
5| 3| 15  
10| 2| 20  
3| 6| 18  
8| 5| 40  
  
The results of this multiplication query can be effectively visualized using various widgets. A Time Chart widget could show how the product values change over time. For comparing the original values with their products, a Table widget would be most appropriate, allowing side-by-side comparison of the input fields and their calculated results.
