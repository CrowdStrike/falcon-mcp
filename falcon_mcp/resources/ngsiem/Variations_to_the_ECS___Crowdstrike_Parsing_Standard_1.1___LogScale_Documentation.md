# Variations to the ECS | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-ecs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

## Variations to the ECS

See [ECS Categorization fields](https://www.elastic.co/guide/en/ecs/current/ecs-category-field-values-reference.html) for more detail on ECS fields. CPS compliant parsers deviate from ECS in the following ways: 

  * Fields which parsers use as tags have their names prefixed with # during ingestion. 

  * The field event.original is not present, since LogScale uses [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) instead. 

  * The field event.ingested is not present, since LogScale uses [@ingesttimestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp) instead. 

  * The field [@timestamp](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) contains a Unix timestamp, rather than a human readable timestamp. 

  * The field event.code is not present. The value from event.code can still be available to use in a vendor-specific field, e.g. Vendor.event_type. 

  * The [related fields](https://www.elastic.co/guide/en/ecs/current/ecs-related.html) are not present. 

  * The following fields have their values lowercased by the `en-us` locale. 

    * *.address 

    * *.domain 

    * email.*.address

    * event.module

    * event.dataset

    * Vendor

    * *.email

    * host.hostname

    * *.hash.*
