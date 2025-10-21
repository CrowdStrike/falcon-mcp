# Get the Last Element of an Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-getfield-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Get the Last Element of an Array

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    | index := array:length("foo[]")-1
    | fieldName := format("foo[%s]", field=[index])
    | result := getField(fieldName)

### Introduction

Given an event with an array for field foo[x]: 
    
    
    foo['a','b','c','d']

Looks up the value of the field which is part of an array of elements, using [`getField()`](https://library.humio.com/data-analysis/functions-getfield.html) in combination with expressions: first build the string with the field, then perform [`getField()`](https://library.humio.com/data-analysis/functions-getfield.html) in that string to get the result. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | index := array:length("foo[]")-1

Sets the index as the last element of the array (in this case, `[6]`) 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | fieldName := format("foo[%s]", field=[index])

Takes the field index and builds the string foo[6] using [`format()`](https://library.humio.com/data-analysis/functions-format.html)

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | result := getField(fieldName)

Provides the value of the field whose name is foo[6]

  5. Event Result set.




### Summary and Results

The output is displayed as follows, where the last column shows the value of fieldName column (which is foo[3]) as the result: 

@timestamp| @rawstring| @timestamp.nanos| fieldName| foo[0]| foo[1]| foo[2]| foo[3]| index| result  
---|---|---|---|---|---|---|---|---|---  
2024-03-01T08:43:12| {"foo": ["a","b","c","d"]}| 0| foo[3]| a| b| c| d| 3| d
