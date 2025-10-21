# Understanding Field Mapping Requirements | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-field-aliasing-mapping-requirements.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

/ [Field Aliasing](searching-data-field-aliasing.html)

### Understanding Field Mapping Requirements

When creating field mappings, there are some requirements to be aware of. 

  * Neither the alias nor the source field can start with `#` or `@`, like #kind or [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp). These are [Metadata Fields](searching-data-event-fields.html#searching-data-event-fields-metadata "Metadata Fields") with special meaning in LogScale. 

  * All aliases must be unique. 

  * The tag conditions cannot be conflicting. For example, it is not possible to have both **`#vendor=A`** and **`#vendor=B`** as conditions on the same mapping. More details on tag conditions are described in [Understanding Schema Requirements](searching-data-field-aliasing-schema-requirements.html "Understanding Schema Requirements").
