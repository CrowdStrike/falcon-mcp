# Extract the Top Most Viewed Pages of a Website | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-top-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract the Top Most Viewed Pages of a Website

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    regex(regex="/.*/(?<url_page>\S+\.page)", field=url)
    | top(url_page, limit=12, rest=others)

### Introduction

Your LogScale repository is ingesting log entries from a web server for a photography site. On this site there are several articles about photography. The URL for articles on this site ends with the extension, `.page` instead of `.html`. 

You want to extract the page users viewed and then list the top most viewed pages. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         regex(regex="/.*/(?<url_page>\S+\.page)", field=url)

Extracts the page viewed by users by returning the name of the file from the url field and storing that result in a field labeled, url_page. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | top(url_page, limit=12, rest=others)

Lists the top most viewed pages. The first parameter given is that url_page field coming from the first line of the query. The second parameter is to limit the results to the top twelve — instead of the default limit of ten. Because we're curious of how many pages were viewed during the selected period that were not listed in the top twelve, the rest parameter is specified with the label to use. 

  4. Event Result set.




### Summary and Results

The table displays the matches from the most viewed pages during the selected period to the least — limited to the top twelve. 

url_page| _count  
---|---  
home.page| 51  
index.page| 21  
home-studio.page| 10  
a-better-digital-camera.page| 7  
is-film-better.page| 6  
leica-q-customized.page| 6  
student-kit.page| 4  
focusing-screens.page| 4  
changing-images-identity.page| 2  
others| 27
