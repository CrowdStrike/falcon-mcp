# CPS Migration | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-migration.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

## CPS Migration

CrowdStrike Parsing Standard (CPS) builds on the [Elastic Common Schema (ECS) 8.x](https://www.elastic.co/guide/en/ecs/current/index.html). ECS isn't specific to any data store, which gives us a lot of flexibility. This page aims to help you transition from our previous interpretation of ECS to CPS. See [_Variations to the ECS_](pasta-ecs.html "Variations to the ECS") for more general details on the differences between ECS and CPS. 

CPS-compliant parsers use [tags](https://library.humio.com/logscale-architecture/training-arch-op-ingest-ingest.html#training-arch-op-ingest-ingest-tags) for these additional fields: 

  * #ecs.version

  * #event.dataset

  * #event.kind

  * #event.module

  * #observer.type




For writing queries and detections that means that instead of: 

logscale
    
    
    observer.type = "firewall"

Your query should follow this format: 

logscale
    
    
    #observer.type = "firewall"

Fields which have been renamed: 

  * Parser_version is now Parser.version




Fields with different normalization applied: 

Field name |  CPS 0.1 |  CPS 1.0   
---|---|---  
*.address |  No normalization |  Lowercasing by `en-us`  
*.domain |  No normalization |  Lowercasing by `en-us`  
email.*.address |  No normalization |  Lowercasing by `en-us`  
host.hostname |  No normalization |  Lowercasing by `en-us`  
*.hash.* |  No normalization |  Lowercasing by `en-us`  
event.module |  No normalization |  See [_event.module Guidelines_](pasta-event-module.html "event.module Guidelines") .   
event.dataset |  No normalization |  See rules for that field in the standard   
  
Fields which have been removed: 

  * The related.* fields (no direct replacement) 

  * Product field (replaced by event.module and event.dataset)
