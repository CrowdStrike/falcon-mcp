# Create Sankey Diagram Calculating Edge Thickness | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-sankey-weight.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Sankey Diagram Calculating Edge Thickness

Create a Sankey diagram calculating the edge thickness using the [`sankey()`](https://library.humio.com/data-analysis/functions-sankey.html) function with an aggregator 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    sankey(source="src", target="dst", weight=(sum(cnt)))

### Introduction

The [`sankey()`](https://library.humio.com/data-analysis/functions-sankey.html) function is used to create a Sankey diagram to vizualise flow relationships between nodes. The input data must be compatible with the [Sankey Diagram](https://library.humio.com/data-analysis/widgets-sankey.html), meaning that the event set must contain source field, target field, and weight field. For more information about Sankey Diagram Widgets, see [Sankey Diagram](https://library.humio.com/data-analysis/widgets-sankey.html). 

In this example, the [`sankey()`](https://library.humio.com/data-analysis/functions-sankey.html) function is used with the [_`weight`_](https://library.humio.com/data-analysis/functions-sankey.html#query-functions-sankey-weight) parameter to show the edge thickness of the fields cnt (count), dst (destination), and src (source) in a Sankey diagram. Edge thickness in a Sankey diagram represents the magnitude or quantity of flow between nodes. 

The `edge` is the connecting line between source and target nodes, and the `thickness` represents the weightend value of that connection. 

Example incoming data might look like this: 

cnt| dst| src  
---|---|---  
12| apples| john  
1| bananas| john  
1| apples| joe  
1| apples| sarah  
1| apples| sarah  
1| apples| sarah  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sankey(source="src", target="dst", weight=(sum(cnt)))

Creates a Sankey diagram showing the sources on the left side (john, joe, sarah), and the targets on the right side (apples, bananas), and then provides the edge thickness based on the sum. 

The default [_`weight`_](https://library.humio.com/data-analysis/functions-sankey.html#query-functions-sankey-weight) parameter is [`count()`](https://library.humio.com/data-analysis/functions-count.html). 

  3. Event Result set.




### Summary and Results

The query is used to create a Sankey diagram showing the sources on the left side (john, joe, sarah), and the targets on the right side (apples, bananas), and then display the edge thickness using the [_`weight`_](https://library.humio.com/data-analysis/functions-sankey.html#query-functions-sankey-weight) parameter. In this example, the thickest edge is `john → apples (12)`, the medium edge is `sarah → apples (3)`, and the thin edges are `joe → apples (1)` and `john → bananas (1)`. 

The query is useful for rendering results as a two-level Sankey diagram and visualize flow relationships between nodes. It shows proportional relationships between data categories. 

Sample output from the incoming example data: 

source| target| weight  
---|---|---  
joe| apples| 1  
john| apples| 12  
john| bananas| 1  
sarah| apples| 3  
  
![Showing Edge Thickness with Sankey\(\)](images/sankey-weight-count-aggregator.png)  
---
