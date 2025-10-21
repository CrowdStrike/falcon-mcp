# Find Union of Array Over multiple Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-union-newarray.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Union of Array Over multiple Events

Find union of an array over multiple events using the [`array:union()`](https://library.humio.com/data-analysis/functions-array-union.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:union(mailto, as=unique_mails)

### Introduction

Arrays are handy when you want to work with multiple values of the same data type. The [`array:union()`](https://library.humio.com/data-analysis/functions-array-union.html) function is used to find distinct values of an array over multiple events. One important feature of UNION is, that it removes duplicate rows from the combined data meaning if there are repetitions, then only one element occurrence should be in the union. 

Example incoming data might look like this: 

mailto[0]| mailto[1]  
---|---  
foo@example.com| bar@example.com  
bar@example.com|   
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:union(mailto, as=unique_mails)

Searches in the mailto array across multiple events and returns the union of element values in a new array, where the unique emails will appear only once. In this case creating a unique list of email addresses in a single array. 

  3. Event Result set.




### Summary and Results

The query is used to search for and eliminate duplicates of e-mail addresses in arrays/combined datasets. 

Sample output from the incoming example data: 

unique_mails[0]| unique_mails[1]  
---|---  
bar@example.com| foo@example.com
