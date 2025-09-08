# Changelog

## [0.3.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.2.0...v0.3.0) (2025-09-08)


### Features

* **module/discover:** Add unmanaged assets search tool to Discover module ([#132](https://github.com/CrowdStrike/falcon-mcp/issues/132)) ([1c7a798](https://github.com/CrowdStrike/falcon-mcp/commit/1c7a7985637fe81c789ac7b0912f748d135238a3))
* **modules/discover:** add new discover module ([#131](https://github.com/CrowdStrike/falcon-mcp/issues/131)) ([2862361](https://github.com/CrowdStrike/falcon-mcp/commit/2862361b8d0402ab7db4458794eb2b9bf62ef829))
* **modules/idp:** Add geolocation info to entities and timeline in i… ([#124](https://github.com/CrowdStrike/falcon-mcp/issues/124)) ([31bb268](https://github.com/CrowdStrike/falcon-mcp/commit/31bb268070a55cd9a0dc52cc3eab566a65dd5ac3))
* **modules/idp:** Add geolocation info to entities and timeline in idp module ([#121](https://github.com/CrowdStrike/falcon-mcp/issues/121)) ([31bb268](https://github.com/CrowdStrike/falcon-mcp/commit/31bb268070a55cd9a0dc52cc3eab566a65dd5ac3))
* **modules/serverless:** add serverless module ([#127](https://github.com/CrowdStrike/falcon-mcp/issues/127)) ([0d7b7b3](https://github.com/CrowdStrike/falcon-mcp/commit/0d7b7b3e33b05541a9507278861d37621d32dfaa))


### Bug Fixes

* fix incorrect module registration assumptions ([#153](https://github.com/CrowdStrike/falcon-mcp/issues/153)) ([bd3aa95](https://github.com/CrowdStrike/falcon-mcp/commit/bd3aa95706a2a35004d6c3c95dbbddd9e8fcffcf))
* **modules/identity:** add missing scope for Identity Protection module ([#148](https://github.com/CrowdStrike/falcon-mcp/issues/148)) ([791a262](https://github.com/CrowdStrike/falcon-mcp/commit/791a2621ed97d20553c0b0d98c6e0690a165208a))

## [0.2.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.1.0...v0.2.0) (2025-08-07)


### Features

* add origins to intel fql guide ([#89](https://github.com/CrowdStrike/falcon-mcp/issues/89)) ([c9a147e](https://github.com/CrowdStrike/falcon-mcp/commit/c9a147eef3f1c991eebc5c2e63781f8ab0eda311))
* disable telemetry ([#102](https://github.com/CrowdStrike/falcon-mcp/issues/102)) ([feb4507](https://github.com/CrowdStrike/falcon-mcp/commit/feb450797b981f9b9dd768e54cb7419f42cdfc90))
* **modules/sensorusage:** add new sensor usage module ([#101](https://github.com/CrowdStrike/falcon-mcp/issues/101)) ([ad97eb8](https://github.com/CrowdStrike/falcon-mcp/commit/ad97eb853f45b3d37af1a9b447531eb859201a0d))
* **resources/spotlight:** FQL filter as tuples ([#91](https://github.com/CrowdStrike/falcon-mcp/issues/91)) ([d9664a6](https://github.com/CrowdStrike/falcon-mcp/commit/d9664a6e37bafa102e1fea1ff109843c4ba9437d))
* **server:** add distinct tools for active vs available modules ([#103](https://github.com/CrowdStrike/falcon-mcp/issues/103)) ([f5f941a](https://github.com/CrowdStrike/falcon-mcp/commit/f5f941a28e9f2e6765d9de0fd060580274d7baab))


### Bug Fixes

* **resources/detections:** added severity_name over severity level and cleaned up example filters ([#93](https://github.com/CrowdStrike/falcon-mcp/issues/93)) ([5f4b775](https://github.com/CrowdStrike/falcon-mcp/commit/5f4b7750ad87475a3ec59f2b493db82193b7358d))


### Refactoring

* remove all return statements from tool docstrings ([#117](https://github.com/CrowdStrike/falcon-mcp/issues/117)) ([80250bb](https://github.com/CrowdStrike/falcon-mcp/commit/80250bb23da4029f0c8bb812cc6334aa7b36673d))
* remove mention to Host from FQL guide ([cf82392](https://github.com/CrowdStrike/falcon-mcp/commit/cf82392cc9f299334ae5cf7a07bd42a81b01f607))
* **resources/cloud:** remove mention to Host from FQL guide ([#76](https://github.com/CrowdStrike/falcon-mcp/issues/76)) ([81ec4de](https://github.com/CrowdStrike/falcon-mcp/commit/81ec4de3c121d407290dde6965942da26478f652))
* **resources/cloud:** use new tuple methodology to create filters ([#95](https://github.com/CrowdStrike/falcon-mcp/issues/95)) ([fd5cce7](https://github.com/CrowdStrike/falcon-mcp/commit/fd5cce7ed458b99f6aa89c4f9cfed0823e51290f))
* **resources/detections:** update guide to be more accurate ([#83](https://github.com/CrowdStrike/falcon-mcp/issues/83)) ([4ff2144](https://github.com/CrowdStrike/falcon-mcp/commit/4ff2144bbf2af3c2db3d2d8e5351c075cee7f610))
* **resources/detections:** use new tuple method for fql detections table ([#97](https://github.com/CrowdStrike/falcon-mcp/issues/97)) ([f328b79](https://github.com/CrowdStrike/falcon-mcp/commit/f328b79cbdcac9e5a1e29cbf11fc517c19e24606))
* **resources/hosts:** tested and updated fql filters and operator support for hosts module ([#63](https://github.com/CrowdStrike/falcon-mcp/issues/63)) ([e0b971c](https://github.com/CrowdStrike/falcon-mcp/commit/e0b971c6b4e4dcda693ea7f8407a21a3e847a1dc))
* **resources/hosts:** use new tuple methodology to create filters ([#96](https://github.com/CrowdStrike/falcon-mcp/issues/96)) ([da38d69](https://github.com/CrowdStrike/falcon-mcp/commit/da38d6904d25ccf8fcdfc8aef62a762acc89507d))
* **resources/incidents:** use new tuple methodology to create filters ([#98](https://github.com/CrowdStrike/falcon-mcp/issues/98)) ([a9ba2f7](https://github.com/CrowdStrike/falcon-mcp/commit/a9ba2f7ba94fe1b7b6108d5e89e4c767afad5657))
* **resources/intel:** use new tuple methodology to create filters ([#99](https://github.com/CrowdStrike/falcon-mcp/issues/99)) ([cf0c19e](https://github.com/CrowdStrike/falcon-mcp/commit/cf0c19ea77b21b8e1590c5642a6aa3de6dbd1a14))
* standardize parameter consistency across all modules ([#106](https://github.com/CrowdStrike/falcon-mcp/issues/106)) ([3c9c299](https://github.com/CrowdStrike/falcon-mcp/commit/3c9c29946942941b50d1fbcf9d640329ea8bc84a))

## 0.1.0 (2025-07-16)


### Features

* add Docker support ([#19](https://github.com/crowdstrike/falcon-mcp/issues/19)) ([f60adc1](https://github.com/crowdstrike/falcon-mcp/commit/f60adc1c1e7e0a441a57d671fa44bb430b66280d))
* add E2E testing ([#16](https://github.com/crowdstrike/falcon-mcp/issues/16)) ([c8a1d18](https://github.com/crowdstrike/falcon-mcp/commit/c8a1d18400fc5d89ef26c7cbe01fe4d46628fdff))
* add filter guide for all tools which have filter param ([#46](https://github.com/crowdstrike/falcon-mcp/issues/46)) ([61ffde9](https://github.com/crowdstrike/falcon-mcp/commit/61ffde90062644bb6014bb89c8b50ec904c728d5))
* add hosts module ([#42](https://github.com/crowdstrike/falcon-mcp/issues/42)) ([9375f4b](https://github.com/crowdstrike/falcon-mcp/commit/9375f4b2399b3ed793d548a498dc132e69ef6081))
* add intel module ([#22](https://github.com/crowdstrike/falcon-mcp/issues/22)) ([6da3359](https://github.com/crowdstrike/falcon-mcp/commit/6da3359e3890d6ee218b105f4342a1ae13690e79))
* add resources infrastructure ([#39](https://github.com/crowdstrike/falcon-mcp/issues/39)) ([2629eae](https://github.com/crowdstrike/falcon-mcp/commit/2629eaef671f75d244f355d43c3e18cad47ee488))
* add spotlight module ([#58](https://github.com/crowdstrike/falcon-mcp/issues/58)) ([713b551](https://github.com/crowdstrike/falcon-mcp/commit/713b55193141fc5d71f3bdc273d960c20e99bff8))
* add streamable-http transport with Docker support and testing ([#24](https://github.com/crowdstrike/falcon-mcp/issues/24)) ([5e44e97](https://github.com/crowdstrike/falcon-mcp/commit/5e44e9708bcccd2580444ffcaf27b03fb6716c9d))
* add user agent ([#68](https://github.com/crowdstrike/falcon-mcp/issues/68)) ([824a69f](https://github.com/crowdstrike/falcon-mcp/commit/824a69f23211cb1e0699332fa07b453bbf0401b4))
* average CrowdScore ([#20](https://github.com/crowdstrike/falcon-mcp/issues/20)) ([6580663](https://github.com/crowdstrike/falcon-mcp/commit/65806634d49248c6b59ef509eadbf4d2b64145f1))
* cloud module ([#56](https://github.com/crowdstrike/falcon-mcp/issues/56)) ([7f563c2](https://github.com/crowdstrike/falcon-mcp/commit/7f563c2e0b5afa35af3d9dbfb778f07b014812ab))
* convert fql guides to resources ([#62](https://github.com/crowdstrike/falcon-mcp/issues/62)) ([63bff7d](https://github.com/crowdstrike/falcon-mcp/commit/63bff7d3a87ea6c07b290f0c610e95e3a4c8423d))
* create _is_error method ([ee7bd01](https://github.com/crowdstrike/falcon-mcp/commit/ee7bd01d691a2cd6a74c2a9c50f406f3bd6e09de))
* flexible tool input parsing ([#41](https://github.com/crowdstrike/falcon-mcp/issues/41)) ([06287fe](https://github.com/crowdstrike/falcon-mcp/commit/06287feaccf41f4c41d587c9ab2f0a874382455b))
* idp support domain lookup and input sanitization ([#73](https://github.com/crowdstrike/falcon-mcp/issues/73)) ([9d6858c](https://github.com/crowdstrike/falcon-mcp/commit/9d6858cd7d0f97a1fbcca3858cafccf688e73da6))
* implement lazy module discovery ([#37](https://github.com/crowdstrike/falcon-mcp/issues/37)) ([a38c949](https://github.com/crowdstrike/falcon-mcp/commit/a38c94973aae3ebdc5b5f51f0980b0266c287680))
* implement lazy module discovery approach ([a38c949](https://github.com/crowdstrike/falcon-mcp/commit/a38c94973aae3ebdc5b5f51f0980b0266c287680))
* initial implementation for the falcon-mcp server ([#4](https://github.com/crowdstrike/falcon-mcp/issues/4)) ([773ecb5](https://github.com/crowdstrike/falcon-mcp/commit/773ecb54f5c7ef7760933a5c12b473df953ca85c))
* refactor to use falcon_mcp name and absolute imports ([#52](https://github.com/crowdstrike/falcon-mcp/issues/52)) ([8fe3f2d](https://github.com/crowdstrike/falcon-mcp/commit/8fe3f2d28573258a620c50270cd23c56aaf4d5fb))


### Bug Fixes

* conversational incidents ([#21](https://github.com/crowdstrike/falcon-mcp/issues/21)) ([ee7bd01](https://github.com/crowdstrike/falcon-mcp/commit/ee7bd01d691a2cd6a74c2a9c50f406f3bd6e09de))
* count number of tools correctly ([#72](https://github.com/crowdstrike/falcon-mcp/issues/72)) ([6c2284e](https://github.com/crowdstrike/falcon-mcp/commit/6c2284e2bac220bfc55b9aea1b416300dbceffb6))
* discover modules in examples ([#31](https://github.com/crowdstrike/falcon-mcp/issues/31)) ([e443fc8](https://github.com/crowdstrike/falcon-mcp/commit/e443fc8348b8aa8c79c17733833b0cb3509d7451))
* ensures proper lists are passed to module arg + ENV VAR support for args ([#54](https://github.com/crowdstrike/falcon-mcp/issues/54)) ([9820310](https://github.com/crowdstrike/falcon-mcp/commit/982031012184b4fe5d5054ace41a4abcac0ff86b))
* freshen up e2e tests ([#40](https://github.com/crowdstrike/falcon-mcp/issues/40)) ([7ba3d86](https://github.com/crowdstrike/falcon-mcp/commit/7ba3d86faed06b4033074bbed0eb5410d87f117f))
* improve error handling and fix lint issue ([#69](https://github.com/crowdstrike/falcon-mcp/issues/69)) ([31672ad](https://github.com/crowdstrike/falcon-mcp/commit/31672ad20a7a78f9edb5e7d5f7e5d610bf8aafb6))
* lock version for mcp-use to 1.3.1 ([#47](https://github.com/crowdstrike/falcon-mcp/issues/47)) ([475fe0a](https://github.com/crowdstrike/falcon-mcp/commit/475fe0a59879a5c53198ebd5e9b548d2fdfd9538))
* make api scope names the UI name to prevent confusion ([#67](https://github.com/crowdstrike/falcon-mcp/issues/67)) ([0089fec](https://github.com/crowdstrike/falcon-mcp/commit/0089fec425c5d1a58e15ebb3d6262cfa21b61931))
* return types for incidents ([ee7bd01](https://github.com/crowdstrike/falcon-mcp/commit/ee7bd01d691a2cd6a74c2a9c50f406f3bd6e09de))


### Documentation

* major refinements to README  ([#55](https://github.com/crowdstrike/falcon-mcp/issues/55)) ([c98dde4](https://github.com/crowdstrike/falcon-mcp/commit/c98dde4a35491806a27bc1ef3ec53e184810b7b9))
* minor readme updates ([7ad3285](https://github.com/crowdstrike/falcon-mcp/commit/7ad3285a942917502cebd8bf1bf067db12a0d6c6))
* provide better clarity around using .env ([#71](https://github.com/crowdstrike/falcon-mcp/issues/71)) ([2e5ec0c](https://github.com/crowdstrike/falcon-mcp/commit/2e5ec0cfd5ba918625481b0c4ea75bf161a3a606))
* update descriptions for better clarity ([#49](https://github.com/crowdstrike/falcon-mcp/issues/49)) ([1fceee1](https://github.com/crowdstrike/falcon-mcp/commit/1fceee1070d04da20fea8e1c19c0c4e286e67828))
* update readme ([#64](https://github.com/crowdstrike/falcon-mcp/issues/64)) ([7b21c1b](https://github.com/crowdstrike/falcon-mcp/commit/7b21c1b8f42a33c3704e116a56e13af6108609aa))
