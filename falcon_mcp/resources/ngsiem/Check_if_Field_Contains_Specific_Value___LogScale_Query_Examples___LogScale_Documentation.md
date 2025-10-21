# Check if Field Contains Specific Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-test-compare-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check if Field Contains Specific Value

Check if field contains specific value using [`test()`](https://library.humio.com/data-analysis/functions-test.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00;

logscale
    
    
    test(myField == "myValue")

### Introduction

The [`test()`](https://library.humio.com/data-analysis/functions-test.html) function can be used to make comparisons between one field and one value, and it can also compare more fields and their respective values. 

In this example, the [`test()`](https://library.humio.com/data-analysis/functions-test.html) function is used to check if a field contains a specific value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         test(myField == "myValue")

Returns all events where field myField holds the specific value myOtherField. Notice the use of double-quotes. If the string had been `test(myField == myOtherField)`, then it would have returned results where the fields contained the same values and not a specific value. 

  3. Event Result set.




### Summary and Results

The query is used to check if a field contains a specific value. The function syntax with [`test()`](https://library.humio.com/data-analysis/functions-test.html) does not support fields with space. For example, `test("f o o" == "bar")` compares the two values, not a field named f o o. 

The syntax form, `myField = myValue` is the preferred method for performance reasons.
