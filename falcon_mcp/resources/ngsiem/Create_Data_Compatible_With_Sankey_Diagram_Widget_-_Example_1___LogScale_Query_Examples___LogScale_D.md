# Create Data Compatible With Sankey Diagram Widget - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-sankey-url-http.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Data Compatible With Sankey Diagram Widget - Example 1

Create data compatible with sankey diagram widget using the [`sankey()`](https://library.humio.com/data-analysis/functions-sankey.html) function to show flow relationship 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    type=accesslog
    | sankey(source=method, target=url)

### Introduction

A sankey diagram widget is a visualization used to depict a flow from one set of values to another. 

In this example, the [`sankey()`](https://library.humio.com/data-analysis/functions-sankey.html) function is used to produce sankey compatible data for a webserver log showing wich URLs matches the HTTP methods. 

Example incoming event data might look like this: 

type| timestamp| method| url  
---|---|---|---  
accesslog| 2025-05-02 11:45:23| GET| /api/users  
accesslog| 2025-05-02 11:45:30| POST| /api/users  
accesslog| 2025-05-02 11:46:12| GET| /api/products  
accesslog| 2025-05-02 11:46:45| PUT| /api/users  
accesslog| 2025-05-02 11:47:01| DELETE| /api/users  
accesslog| 2025-05-02 11:47:33| GET| /api/orders  
accesslog| 2025-05-02 11:48:02| POST| /api/orders  
accesslog| 2025-05-02 11:48:15| GET| /api/cart  
accesslog| 2025-05-02 11:48:45| POST| /api/login  
accesslog| 2025-05-02 11:49:01| GET| /api/logout  
accesslog| 2025-05-02 11:49:30| GET| /api/users  
accesslog| 2025-05-02 11:50:00| POST| /api/products  
accesslog| 2025-05-02 11:50:23| PUT| /api/products  
accesslog| 2025-05-02 11:50:45| GET| /api/users  
accesslog| 2025-05-02 11:51:12| POST| /api/cart  
accesslog| 2025-05-02 11:51:33| GET| /api/users  
accesslog| 2025-05-02 11:52:01| GET| /api/products  
accesslog| 2025-05-02 11:52:30| POST| /api/orders  
accesslog| 2025-05-02 11:53:00| DELETE| /api/products  
accesslog| 2025-05-02 11:53:15| GET| /api/dashboard  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         type=accesslog

Filters for all webserver logs. The access log is a list of all requests for individual files (for example HTML files) that users have made from a website, therefore, webserver logs provide valuable business insight. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | sankey(source=method, target=url)

Produces sankey compatible data for a webserver log showing wich URLs matches the HTTP methods. It shows how traffic is distributed across different endpoints. 

Note that source and target are required fields to be able to produce a Sankey Diagram. 

  4. Event Result set.




### Summary and Results

The query is used to produce data compatible with sankey diagram widgets, in this example visualizing the relationship between HTTP methods and URLs. 

Sankey diagram widgets are a powerful data visualization tool used to represent the flow of values between stages, offering valuable insights into the flow of data. When used with well-structured data, they can help identify patterns, bottlenecks, and significant resource allocation trends. 

Sankey diagram widgets are useful in case you want to show complex processes visually, with a focus on a single aspect or resource required to be highlighted. Sankey diagram widgets can also be used to reveal inconsistent data, as the visualization of data inconsistencies makes detection easier. 

![Showing Relationship with sankey\(\)](images/sankey-url-http.png)  
---
