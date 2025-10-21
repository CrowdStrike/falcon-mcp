# Set Values for Multiple Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-setfield-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set Values for Multiple Fields

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[(Function)] 4[(Function)] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result

logscale
    
    
    item := 4
    | bar := "baz"
    | setField(target=bar, value=item + 10)
    | setField(target="foo", value=item + 20)
    | setField(target="baaz", value=if(item == 4, then="OK", else="not OK"))

### Introduction

Set the value of more fields as the result of several expressions. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[(Function)] 4[(Function)] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         item := 4

In a `test` event where field item is set to `4`: 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[(Function)] 4[(Function)] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | bar := "baz"

Points field bar to field "baz": 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[(Function)] 4[(Function)] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | setField(target=bar, value=item + 10)

Takes field bar as the target, gets the field pointed to by bar (baz) and sets its value as the result of the expression `value of item + 10`. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[(Function)] 4[(Function)] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | setField(target="foo", value=item + 20)

Takes field foo as the target, sets its value as the result of the expression "value of item \+ 20": 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] 3[(Function)] 4[(Function)] 5[(Function)] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | setField(target="baaz", value=if(item == 4, then="OK", else="not OK"))

Adds an [`if()`](https://library.humio.com/data-analysis/functions-if.html) function whose condition will set the value of the new target field baaz: for example, if item is equal to `4`, then the value of field baaz is `OK`, otherwise `not OK`. 

  7. Event Result set.




### Summary and Results

We look at different target fields to set their values as the result of a given expression. Functions can be added as part of the expression in the [_`value`_](https://library.humio.com/data-analysis/functions-setfield.html#query-functions-setfield-value) parameter, to determine the value of another target expression. 

baaz| bar| bar| baz| foo| item  
---|---|---|---|---|---  
OK| baz| baz| 14| 24| 4
