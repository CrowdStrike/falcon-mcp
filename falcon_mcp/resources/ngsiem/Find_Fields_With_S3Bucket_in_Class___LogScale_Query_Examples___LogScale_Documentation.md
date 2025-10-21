# Find Fields With S3Bucket in Class | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-wildcard-6.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Fields With S3Bucket in Class

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    wildcard(field=class, pattern="*S3Bucket*", ignoreCase=true)
    | groupBy(class)

### Introduction

Find all events containing any `S3Bucket` item (and all before and after) in their class, and count the occurrences for each class that is found. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         wildcard(field=class, pattern="*S3Bucket*", ignoreCase=true)

Searches the incoming data to list all events having S3Bucket (or everything around it, case-insensitive) in their string. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(class)

Takes the events extracted from the search and group them by the class field. 

  4. Event Result set.




### Summary and Results

The result is an aggregated count of all events matching anything with `S3Bucket`, case-insensitive, in the class field. 

class| _count  
---|---  
c.h.b.s.S3BucketStorageCleaningJob| 197  
c.h.b.s.S3BucketStorageFileUpLoader| 2329  
c.h.b.s.S3BucketStorageUploadJob| 3869  
  
![Searching S3Bucket with wildcard\(\)](images/query-functions/wildcard-s3-bucket.png)  
---  
  
**Figure 1. Search S3Bucket With wildcard()**
