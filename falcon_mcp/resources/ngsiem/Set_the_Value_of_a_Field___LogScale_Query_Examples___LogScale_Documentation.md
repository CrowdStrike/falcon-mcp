# Set the Value of a Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-setfield-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set the Value of a Field

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    item := 4
    | setField(target="foo", value=item + 10)

### Introduction

Set the value of a target field as the result of an expression. This is equivalent to: 

logscale
    
    
    item := 4
    | foo := item + 10

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         item := 4

In a `test` event the field item is set to `4`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | setField(target="foo", value=item + 10)

Sets the value of the target field foo as the result of the expression `value of item + 10`. 

  4. Event Result set.




### Summary and Results

foo| item  
---|---  
14| 4
