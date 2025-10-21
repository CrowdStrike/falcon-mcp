# Check if Fields Contain Same Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-test-compare-length.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check if Fields Contain Same Value

Search for more fields with same length using the test() function with length() 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00;

logscale
    
    
    test(length(userid) == length(method))

### Introduction

The [`test()`](https://library.humio.com/data-analysis/functions-test.html) function can be used to make comparisons between one field and one value, and it can also compare more fields and their respective values. 

In this example, the [`test()`](https://library.humio.com/data-analysis/functions-test.html) function is used with [`length()`](https://library.humio.com/data-analysis/functions-length.html) to search for events where the userid field and method field have the same length. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         test(length(userid) == length(method))

Returns all events where field userid has the same length as the method field. This could for example be events with `Chad` and _`POST`_ , and `Peter` and _`PATCH`_. 

  3. Event Result set.




### Summary and Results

The query is used to compare more fields and their respective values.
