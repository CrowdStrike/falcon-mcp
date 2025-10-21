# List URLs Not Found | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-top-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## List URLs Not Found

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    statuscode = "404"
    | top(url, limit=20)

### Introduction

You want to get a list of URLs that users attempted to view, but the web server could not find them. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         statuscode = "404"

Filters only events in which the statuscode is 404: that is the HTTP code which indicates that the requested URL was not found. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | top(url, limit=20)

Pipe the events to the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function to group the results on the value of the urlurl field and to list the top twenty. 

  4. Event Result set.




### Summary and Results

The results show a few attempts to access pages like `wp-login.php` and similar pages. These are attempts to log into WordPress, Drupal, and other content management systems. Since this particular web server does not use a CMS, these pages don't exist on the server and are indications of failed hacker attempts. 

url| _count  
---|---  
/.env| 962  
/favicon.ico| 67  
/api/.env| 22  
/core/.env| 25  
/backend/.env| 25  
/info.php| 19  
/admin/.env| 19  
/user/login| 18
