# Check for AWS Resources in Vendor Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-objectarray-exists-aws-resources.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check for AWS Resources in Vendor Array

Filter events based on specific AWS resource ARNs using the [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    objectArray:exists(array="Vendor.resources[]", condition={Vendor.resources.ARN="arn:aws:*"})

### Introduction

The [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html) can be used to search through arrays and find elements that match specified conditions. It is particularly useful when working with nested JSON data structures containing arrays. 

In this example, the [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html) function is used to filter events where an AWS resource ARN exists within a vendor's resource array that matches a specific pattern. 

Example incoming data might look like this: 

@timestamp| Vendor.resources  
---|---  
2023-06-15T10:00:00Z, [{"ARN": "arn:aws:s3:::bucket1", "Type": "S3"}, {"ARN": "arn:aws:ec2:instance1", "Type": "EC2"}]|   
2023-06-15T10:01:00Z, [{"ARN": "arn:azure:vm1", "Type": "VM"}, {"ARN": "arn:azure:storage1", "Type": "Storage"}]|   
2023-06-15T10:02:00Z, [{"ARN": "arn:aws:lambda:function1", "Type": "Lambda"}, {"ARN": "arn:aws:s3:::bucket2", "Type": "S3"}]|   
2023-06-15T10:03:00Z, [{"ARN": "arn:gcp:instance1", "Type": "VM"}, {"ARN": "arn:gcp:storage1", "Type": "Storage"}]|   
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         objectArray:exists(array="Vendor.resources[]", condition={Vendor.resources.ARN="arn:aws:*"})

Filters events by checking if any element in the Vendor.resources array contains an ARN field that matches the pattern `arn:aws:*`. The [_`array`_](https://library.humio.com/data-analysis/functions-objectarray-exists.html#query-functions-objectarray-exists-array) parameter specifies the array to search through, and the [_`condition`_](https://library.humio.com/data-analysis/functions-objectarray-exists.html#query-functions-objectarray-exists-condition) parameter defines the matching criteria. 

  3. Event Result set.




### Summary and Results

The query is used to identify events that contain AWS resources by checking the ARN patterns in the resource array. The [`objectArray:exists()`](https://library.humio.com/data-analysis/functions-objectarray-exists.html) function filters events based on array content matching specific conditions. 

This query is useful, for example, to monitor AWS-specific resources in a multi-cloud environment, audit AWS resource usage, or filter out non-AWS resources from the analysis. 

Sample output from the incoming example data: 

@timestamp| Vendor.resources  
---|---  
2023-06-15T10:00:00Z, [{"ARN": "arn:aws:s3:::bucket1", "Type": "S3"}, {"ARN": "arn:aws:ec2:instance1", "Type": "EC2"}]|   
2023-06-15T10:02:00Z, [{"ARN": "arn:aws:lambda:function1", "Type": "Lambda"}, {"ARN": "arn:aws:s3:::bucket2", "Type": "S3"}]|   
  
Note that only events containing AWS ARNs (starting with "arn:aws:") are included in the results, while events with Azure and GCP resources are filtered out.
