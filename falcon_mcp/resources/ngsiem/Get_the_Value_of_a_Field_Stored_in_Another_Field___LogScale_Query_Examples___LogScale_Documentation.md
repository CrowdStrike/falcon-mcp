# Get the Value of a Field Stored in Another Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-getfield-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Get the Value of a Field Stored in Another Field

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    result := getField("foo")

### Introduction

Given an event with the following fields: 
    
    
    |------------------|
    | foo      | bar   |
    | bar      | 123   |
    | foo      | quux  |
    |------------------|

Do a "direct" lookup where the result is set to the value that is stored in that field, by quoting the string — it takes expressions as input (similar to [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) and [`test()`](https://library.humio.com/data-analysis/functions-test.html) functions): 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         result := getField("foo")

The result is set to the value that is stored in field foo

  3. Event Result set.




### Summary and Results

bar| foo| result  
---|---|---  
123| bar| bar  
<no value>| quux| quux  
  
In the same event, using the same query that does not quote the string: 

logscale
    
    
    result := getField(foo)

will get the value of the field which name is stored at foo, so `123` is stored as the result: 

bar| foo| result  
---|---|---  
123| bar| 123  
<no value>| quux| <no value>  
  
(no result is output for `foo=quux` as `quux` does not exist).
