# Calculate Ingest Queue Compression | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-ingest-queue.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Ingest Queue Compression

Determine the ingest queue compression size 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4{{Aggregate}} 5{{Aggregate}} 6["Drop Event"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> result

logscale
    
    
    #type=humio #kind=metrics
    | name=/^ingest-writer-(?<un>un)?compressed-bytes$/
    | case {
    un=*
    | un := m1;
    comp := m1 }
    | timeChart(function=[sum(un,as=un),sum(comp,as=comp)], minSpan=1m)
    | ratio:=un/comp
    drop([un,comp])

### Introduction

This query is used to calculate ingest queue average compression. A compression ratio is used to express the amount of data that has been saved by compressing. A 10x ratio would mean that 100 GB of data is compressed down to 10 GB of data. This value is discovered by dividing the initial data size by the compressed data size, so for example `100/10`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4{{Aggregate}} 5{{Aggregate}} 6["Drop Event"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=humio #kind=metrics

Filters on all humio records and filters on all metrics within the cluster. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4{{Aggregate}} 5{{Aggregate}} 6["Drop Event"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | name=/^ingest-writer-(?<un>un)?compressed-bytes$/

Filters for the field name where the string starts with `ingest-writer` and calculates the ingest queue average compression. Creates a new field named un if the data is uncompressed by using a regular expression match looking for 'uncompressed-bytes'. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4{{Aggregate}} 5{{Aggregate}} 6["Drop Event"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | case {
         un=*
         | un := m1;
         comp := m1 }

Creates two fields with using the same number from the m1 field, un contains the uncompressed values. comp contains the compressed values. This is achieved by using a `case` statement to look for the un field created in the previous step. In each case the value of the resultant field is the value of the m1 field which is the size of the compressed or uncompressed data. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4{{Aggregate}} 5{{Aggregate}} 6["Drop Event"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | timeChart(function=[sum(un,as=un),sum(comp,as=comp)], minSpan=1m)

Shows the calculated sum of the values in the fields un and comp in buckets of 1 min in a timechart. This shows the comparison between the compressed and uncompressed data, since the incoming data is reported in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repo in pairs of events. 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4{{Aggregate}} 5{{Aggregate}} 6["Drop Event"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | ratio:=un/comp

Compares the two fields un and comp and returns the average compressed size by dividing the sum of the un field with the sum of the comp field. 

  7. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] 4{{Aggregate}} 5{{Aggregate}} 6["Drop Event"] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> 6 6 --> result style 6 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         drop([un,comp])

Discards the un field and the comp field from the results. 

  8. Event Result set.




### Summary and Results

The query is used to calculate the ingest queue average compression using ratio on the sum from two fields. The use of the right compression method is vital for reducing network traffic, CPU and memory usage.
