# Bucket Counts When Using bucket()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-buckets-range.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Bucket Counts When Using [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

**Search Repository:** [humio-metrics](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-metrics.html)

logscale
    
    
    bucket(buckets=24, function=sum("count"))
    | parseTimestamp(field=_bucket,format=millis)

### Introduction

When generating a list of buckets using the [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html) function, the output will always contain one more bucket than the number defined in [_`buckets`_](https://library.humio.com/data-analysis/functions-bucket.html#query-functions-bucket-buckets). This is to accommodate all the values that will fall outside the given time frame across the requested number of buckets. This calculation is due to the events being bound by the bucket in which they have been stored, resulting in [`bucket()`](https://library.humio.com/data-analysis/functions-bucket.html) selecting the buckets for the given time range and any remainder. For example, when requesting 24 buckets over a period of one day in the [humio-metrics](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-metrics.html) repository: 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         bucket(buckets=24, function=sum("count"))

Buckets the events into 24 groups, using the [`sum()`](https://library.humio.com/data-analysis/functions-sum.html) function on the count field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseTimestamp(field=_bucket,format=millis)

Extracts the timestamp from the generated bucket and convert to a date time value; in this example the bucket outputs the timestamp as an epoch value in the _bucket field. 

  4. Event Result set.




### Summary and Results

The resulting output shows 25 buckets, the original 24 requested one additional that contains all the data after the requested timespan for the requested number of buckets. 

_bucket| _sum| @timestamp  
---|---|---  
1681290000000| 1322658945428| 1681290000000  
1681293600000| 1879891517753| 1681293600000  
1681297200000| 1967566541025| 1681297200000  
1681300800000| 2058848152111| 1681300800000  
1681304400000| 2163576682259| 1681304400000  
1681308000000| 2255771347658| 1681308000000  
1681311600000| 2342791941872| 1681311600000  
1681315200000| 2429639369980| 1681315200000  
1681318800000| 2516589869179| 1681318800000  
1681322400000| 2603409167993| 1681322400000  
1681326000000| 2690189000694| 1681326000000  
1681329600000| 2776920777654| 1681329600000  
1681333200000| 2873523432202| 1681333200000  
1681336800000| 2969865160869| 1681336800000  
1681340400000| 3057623890645| 1681340400000  
1681344000000| 3144632647026| 1681344000000  
1681347600000| 3231759376472| 1681347600000  
1681351200000| 3318929777092| 1681351200000  
1681354800000| 3406027872076| 1681354800000  
1681358400000| 3493085788508| 1681358400000  
1681362000000| 3580128551694| 1681362000000  
1681365600000| 3667150316470| 1681365600000  
1681369200000| 3754207997997| 1681369200000  
1681372800000| 3841234050532| 1681372800000  
1681376400000| 1040019734927| 1681376400000
