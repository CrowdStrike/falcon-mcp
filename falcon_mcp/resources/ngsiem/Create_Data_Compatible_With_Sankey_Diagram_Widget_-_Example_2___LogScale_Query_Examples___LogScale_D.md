# Create Data Compatible With Sankey Diagram Widget - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-sankey-url-referrer.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Data Compatible With Sankey Diagram Widget - Example 2

Create data compatible with sankey diagram widget using the [`sankey()`](https://library.humio.com/data-analysis/functions-sankey.html) function to show flow relationship 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    Type=accesslog referrer!="-"
    | sankey(source=referrer, target=url)

### Introduction

A sankey diagram widget is a visualization used to depict a flow from one set of values to another. 

In this example, the [`sankey()`](https://library.humio.com/data-analysis/functions-sankey.html) function is used to produce sankey compatible data for a webserver log showing the URL address (the referrer) of the website that sends users to another website using a link. 

Type| timestamp| method| url| referrer  
---|---|---|---|---  
accesslog| 2025-05-02 11:45:23| GET| /api/users| -  
accesslog| 2025-05-02 11:45:30| POST| /api/users| -  
accesslog| 2025-05-02 11:46:12| GET| /api/products| -  
accesslog| 2025-05-02 11:46:45| PUT| /api/users| -  
accesslog| 2025-05-02 11:47:01| DELETE| /api/users| https://example.com/user  
accesslog| 2025-05-02 11:47:33| GET| /api/orders| -  
accesslog| 2025-05-02 11:48:02| POST| /api/orders| -  
accesslog| 2025-05-02 11:48:15| GET| /api/cart| https://example.com/user  
accesslog| 2025-05-02 11:48:45| POST| /api/login| -  
accesslog| 2025-05-02 11:49:01| GET| /api/logout| https://example.com/login  
accesslog| 2025-05-02 11:49:30| GET| /api/users| -  
accesslog| 2025-05-02 11:50:00| POST| /api/products| -  
accesslog| 2025-05-02 11:50:23| PUT| /api/products| -  
accesslog| 2025-05-02 11:50:45| GET| /api/users| -  
accesslog| 2025-05-02 11:51:12| POST| /api/cart| https://example.com/user  
accesslog| 2025-05-02 11:51:33| GET| /api/users| -  
accesslog| 2025-05-02 11:52:01| GET| /api/products| -  
accesslog| 2025-05-02 11:52:30| POST| /api/orders| -  
accesslog| 2025-05-02 11:53:00| DELETE| /api/products| https://example.com/products  
accesslog| 2025-05-02 11:53:15| GET| /api/dashboard| https://example.com/products  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         Type=accesslog referrer!="-"

Filters for all webserver logs where the referrer is not equal to `-`. It returns all results where the value is not `-`. 

The value `-` is often used by analytics to define an empty value. In this example, we therefore filter for webserver logs where there is referrer information. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | sankey(source=referrer, target=url)

Produces sankey compatible data for a webserver log showing wich target URLs matches the referrer URL. If one URL links to the same website twice, the count of referring pages for that website will be one and the count of backlinks will be two. 

Note that source and target are required fields to be able to produce a Sankey Diagram. 

  4. Event Result set.




### Summary and Results

The query is used to produce data compatible with sankey diagram widgets, showing the referrer URL. The query is useful to get an overview of the webpage that a user was on right before they landed on your page, the target (it shows how users navigate to different URLs on your site). 

![Showing Relationship with sankey\(\)](images/sankey-url-referrer.png)  
---
