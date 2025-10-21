# CrowdStrike Parsing Standard (CPS) 1.1 | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

# CrowdStrike Parsing Standard (CPS) 1.1

Following CrowdStrike Parsing Standard (CPS) helps you ingest data in a way that simplifies writing queries that combine data across different data sources. This page provides you with an introduction on how to write parsers that conform to this standard, focusing on normalization. 

The majority of the parsers on Falcon LogScale [Package Marketplace](https://library.humio.com/integrations/packages-marketplace.html) follow this standard. For overall guidance on writing parsers in LogScale, see [Create a Parser](https://library.humio.com/data-analysis/parsers-create.html) and [Developer Guidelines for Packages](https://library.humio.com/integrations/packages-developer-guidelines.html). 

## What is normalization in LogScale?

Extracting fields and tags during the parsing stage is crucial for search performance. Mapping different vendor field names (for example timestamp or IP) during the parsing stage to a unified field name helps you simplify your queries. Instead of switching between different fields that contain common information, for example ip_source and source-ip depending on the log format, you will be able to use consistent field names across different vendors and different log formats. 

## Why CrowdStrike Parsing Standard (CPS)

The Crowdstrike Parsing Standard builds on the [Elastic Common Schema (ECS)](https://www.elastic.co/docs/reference/ecs). ECS isn't specific to any data store, which provides a lot of flexibility. It's a mature and proven common schema for metrics, logs, traces and resources, managed by the [OpenTelemetry community](https://opentelemetry.io/) which shares our interest in the convergence of observability and security. See [ ECS Categorization fields](https://www.elastic.co/guide/en/ecs/current/ecs-category-field-values-reference.html) for more detail on ECS fields. 

CPS differs from ECS in a number of ways that build on the specifics of LogScale core architecture. For example, parsers that follow CPS make all fields in a log event available as actual LogScale fields, even if they don't match a field in ECS. See [_Variations to the ECS_](pasta-ecs.html "Variations to the ECS") for more details on the differences between ECS and CPS. 

For any given data source, when developing a parser, you can decide which domain specific fields are applicable to the data. 

To create CPS compliant Parsers: 

  1. Use CPS Compliant Parser tags: 

     * #Cps.version

     * #Vendor

     * #ecs.version

     * #event.dataset

     * #event.kind

     * #event.module

     * #event.outcome

     * #observer.type

  2. Your parsers must populate the fields described in [Fields Expected From CPS Compliant Parsers](pasta.html#pasta-parsers "Fields Expected From CPS Compliant Parsers")

  3. Manage any fields which do not match the ECS fields, see [Managing Non ECS Fields](pasta.html#pasta-fields "Managing Non ECS Fields"). 

  4. Add any fields you need to the standard, see [Adding Fields to the Standard](pasta.html#pasta-add "Adding Fields to the Standard"). 




## Fields Expected From CPS Compliant Parsers

These fields define the CPS compliant fields that are expected, and must be created during parsing: 

### Event Categorization Fields

Event categorization fields align with the core ECS categorization rules [here](https://www.elastic.co/docs/reference/ecs/ecs-category-field-values-reference). 

The key fields are: 

  * event.kind corresponds to [Event kind](https://www.elastic.co/docs/reference/ecs/ecs-allowed-values-event-kind) and assigned within LogScale as an array. 

  * event.category corresponds to [Event category](https://www.elastic.co/docs/reference/ecs/ecs-allowed-values-event-category) and assigned within LogScale as an array. 

  * event.type corresponds to [Event type](https://www.elastic.co/docs/reference/ecs/ecs-allowed-values-event-type). 

  * event.outcome corresponds to [Event outcome](https://www.elastic.co/docs/reference/ecs/ecs-allowed-values-event-outcome) is only assigned when an event can logically contain an outcome. 




### ecs.version

This field contains the version of ECS that is being followed by the parser. 

### Cps.version

  * This field contains a `MAJOR.MINOR.PATCH` version number following Semantic Versioning. 

  * The version denotes the version of this standard, which was targeted by the parser during ingest. 




### Parser Version

  * This field contains a `MAJOR.MINOR.PATCH` version number following Semantic Versioning. 

  * This version number is specific to the parser which parsed the event, and not related to e.g. the version of the package the parser may have been installed from. 

  * The rules for updating the version number are: 

    * **Major**

      * Modification of one of the key ECS fields ( event.kind, event.module, event.dataset). 

      * Removal or modification of event.category or event.type

      * Modification of 5 or more unique existing fields (e.g. name changes/value changes) in the dataset 

      * Major overhauls or design changes to the parser 

    * **Minor**

      * Modification of 4 or less unique existing fields that are not a patch/error fix (e.g. fixing misspelling or small accidental issues) 

      * Additional features or fields that do not meet the threshold of a major change 

    * **Patch**

      * Modifications to existing fields or architecture that have minimal impact on the parser (e.g. updating ecs.version) 

      * No extra features or changes, just bug fixes and corrections. This may include misspellings or corrections to field mappings that do not meet the threshold of a minor change. 




#### Vendor

  * If the event was parsed with a parser from a package, the vendor name used here must match the vendor name used in the package scope (e.g. `fortinet` for `fortinet/fortigate`). 

  * If a parser sets any of the following fields, those must be consistent with vendor names used in other CPS-compliant parsers: 

    * observer.vendor

    * vulnerability.scanner.vendor

    * device.manufacturer

  * See, [_Vendor Guidelines_](pasta-vendors.html "Vendor Guidelines"), for guidelines on which vendor name to use. 




#### event.kind

  1. This field shall contain a value representing the type of information the incoming event contains. 

  2. If assigning `event.kind:= "alert"`: 

     * The follow fields are **required** : 

       * event.category[]

       * event.type[]

       * event.severity

This adheres to the Common Information Model mappings and is required for proper detections logic. If these fields are not available then the event should be set to `event.kind := "event"` and not `event.kind:= "alert"`. 

     * event.severity must always map to a value within the range 1-100. The detections logic interprets numerical severities as follows: 

Vendor severity |  Range   
---|---  
Informational |  1-19   
Low |  20-39   
Medium |  40-59   
High |  60-79   
Critical |  80-100   
  



#### event.module

Contains roughly the name of the product or service that the event belongs to. Existing event.module values is reused whenever appropriate. 

#### event.dataset

  * Contains the specific name of the dataset within the module described by event.module, prefixed by the value of event.module with a dot in between. 

  * If it wouldn't contain any information beyond what is present in event.module, the parser doesn't create this field. 

After ingest all the fields in LogScale are prefixed with `#`. 

Example combinations of the above fields in the parser can be: 

**Vendor** |  **event.module** |  **event.dataset**  
---|---|---  
`microsoft` |  `azure` |  `azure.entraid`  
`zscaler` |  `zia` |  `zia.web`  
`cloudflare` |  `zero-trust` |  `zero-trust.network-session`  
  



## Managing Non ECS Fields

CPS compliant parsers strive to make all fields in a log event available as actual LogScale fields, even if they don't match a field in ECS: 

  * If the event contains fields which don't exist in ECS, their name is prefixed with the string literal Vendor. 

This gives the ECS fields the `root` `namespace`, while vendor specific fields can always be found with the Vendor. prefix. 

  * Always keep the original Vendor. field when normalizing third party fields to ECS. 

    * When vendor specific field names are not present in the logs: 

      * If vendor documentation provides field names: 

        * Map values to Vendor. **and** ECS fields. 

      * If vendor documentation _does not_ provide field names: 

        * First try to map to an appropriate ECS field. 

        * If no ECS field exists, create a descriptive Vendor. field name. 

  * Maintain original field names from vendors: 

    * Keep Vendor. field names and values unchanged to ensure direct correlation with source logs. 

    * Exception: Replace spaces with underscores (_) in field names. 

Example: Vendor.User Name should become Vendor.User_Name. 




## Adding Fields to the Standard

When adding new fields to this standard, all fields which are not taken directly from ECS must have a capital letter from the point where they differ from the schema. 

  * Using capital letters for field names follows [the guidance from ECS](https://www.elastic.co/guide/en/ecs/current/ecs-custom-fields-in-ecs.html) on how to add event fields outside the schema. 

  * Example of fully custom field: Parser.version is similar to ecs.version, but the Parser `namespace` is our own, so must start with a capital letter. 

  * Example of extending ECS with custom field: observer.Fictional_field where observer is an existing namespace in the schema, but Fictional_field is our own field inside that namespace.
