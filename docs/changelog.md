<!-- meta:title Changelog -->
<!-- meta:description Release history for the Falcon MCP Server. -->

# Changelog

## [0.15.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.14.0...v0.15.0) (2026-07-20)


### Features

* **modules:** add pagination envelope to search tools ([#470](https://github.com/CrowdStrike/falcon-mcp/issues/470)) ([df8b191](https://github.com/CrowdStrike/falcon-mcp/commit/df8b19182a0833ac9d800937fc5661595d87aa5d))

## [0.14.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.13.0...v0.14.0) (2026-07-16)


### Features

* **cloud:** add falcon_search_cloud_risks, falcon_search_cloud_groups, and falcon_get_cloud_groups tools ([#467](https://github.com/CrowdStrike/falcon-mcp/issues/467)) ([79f4a18](https://github.com/CrowdStrike/falcon-mcp/commit/79f4a18cba3e4b8208be0c903c09f0083ef6a30b))


### Bug Fixes

* **deps:** add cryptography floor constraint for CVE-2026-34180 ([3e43ecb](https://github.com/CrowdStrike/falcon-mcp/commit/3e43ecb9890a501830564f0a88193452f491a4d3))
* **deps:** bump cryptography minimum version ([#458](https://github.com/CrowdStrike/falcon-mcp/issues/458)) ([3e43ecb](https://github.com/CrowdStrike/falcon-mcp/commit/3e43ecb9890a501830564f0a88193452f491a4d3))
* **modules/spotlight:** allow facet to accept a list of values ([#460](https://github.com/CrowdStrike/falcon-mcp/issues/460)) ([31cd989](https://github.com/CrowdStrike/falcon-mcp/commit/31cd989877a9f1bc69927c127c627b73f2ab7895))
* **modules:** restore sort order in two-step search tools ([#463](https://github.com/CrowdStrike/falcon-mcp/issues/463)) ([eff6a6c](https://github.com/CrowdStrike/falcon-mcp/commit/eff6a6c2b9be45d5b9ec67e1cb4cbe8160588819))
* **scheduled_reports:** send body as array in launch_scheduled_report ([#464](https://github.com/CrowdStrike/falcon-mcp/issues/464)) ([3a5d1c9](https://github.com/CrowdStrike/falcon-mcp/commit/3a5d1c97d0fdad24441e34d234c378f527419db6))
* **scheduled_reports:** send request body as array in launch_scheduled_report ([#464](https://github.com/CrowdStrike/falcon-mcp/issues/464)) ([#466](https://github.com/CrowdStrike/falcon-mcp/issues/466)) ([3a5d1c9](https://github.com/CrowdStrike/falcon-mcp/commit/3a5d1c97d0fdad24441e34d234c378f527419db6))

## [0.13.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.12.0...v0.13.0) (2026-06-25)


### Features

* **dynamic:** add dynamic mode to reduce context window usage ([#441](https://github.com/CrowdStrike/falcon-mcp/issues/441)) ([807d3db](https://github.com/CrowdStrike/falcon-mcp/commit/807d3db203dd0d9cd2c04dfa5f8455d971b0a97e))
* **modules/recon:** add Falcon Intelligence Recon module ([#446](https://github.com/CrowdStrike/falcon-mcp/issues/446)) ([f8d4839](https://github.com/CrowdStrike/falcon-mcp/commit/f8d4839de6224e6c052f53238e83257bed3f3a84))


### Bug Fixes

* **deps:** add version floor constraints for pyjwt, idna, requests ([#455](https://github.com/CrowdStrike/falcon-mcp/issues/455)) ([a9536ea](https://github.com/CrowdStrike/falcon-mcp/commit/a9536eadb6c39f7d66d2128251bcbd5fe2280744))
* **modules/detections:** replace verdict param with tags to be inline with ui experience ([#450](https://github.com/CrowdStrike/falcon-mcp/issues/450)) ([c1aee37](https://github.com/CrowdStrike/falcon-mcp/commit/c1aee371b4d9e92aa246b0074b64d1aa7a440faf))
* **modules/ioc:** return delete summary ([#444](https://github.com/CrowdStrike/falcon-mcp/issues/444)) ([df2995a](https://github.com/CrowdStrike/falcon-mcp/commit/df2995a4e2e6948a57738fb8bb3660e0a23d0318))
* **tests/integration:** correct platform field assertion in firewall tests ([#449](https://github.com/CrowdStrike/falcon-mcp/issues/449)) ([3d5a2bb](https://github.com/CrowdStrike/falcon-mcp/commit/3d5a2bb1b1052b026933937ee2bdc30bf846a289)), closes [#448](https://github.com/CrowdStrike/falcon-mcp/issues/448)

## [0.12.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.11.0...v0.12.0) (2026-06-11)


### Features

* **modules/detections:** add update_detections tool ([#439](https://github.com/CrowdStrike/falcon-mcp/issues/439)) ([477c47e](https://github.com/CrowdStrike/falcon-mcp/commit/477c47e4c88d6002642fc9e718a4238939d12322))
* **modules/exclusions:** add unified Exclusions module ([#437](https://github.com/CrowdStrike/falcon-mcp/issues/437)) ([b9b7ea6](https://github.com/CrowdStrike/falcon-mcp/commit/b9b7ea611f7f18be4c2e5e8e29db1578a7d2c84d))
* **modules/host-groups:** add Host Groups module ([#431](https://github.com/CrowdStrike/falcon-mcp/issues/431)) ([5b6e2af](https://github.com/CrowdStrike/falcon-mcp/commit/5b6e2afdfc5dddd032130870e84bce41e23ba234))
* **modules/policies:** add unified Policies module ([#438](https://github.com/CrowdStrike/falcon-mcp/issues/438)) ([7975fa3](https://github.com/CrowdStrike/falcon-mcp/commit/7975fa36e6ab561a49e67bbe64996fbf907d8119))

## [0.11.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.10.0...v0.11.0) (2026-06-03)


### Features

* **client:** add proxy configuration for outbound Falcon API connections ([#408](https://github.com/CrowdStrike/falcon-mcp/issues/408)) ([5ebafe1](https://github.com/CrowdStrike/falcon-mcp/commit/5ebafe1ed417acfd31684929800f23cbd57608af)), closes [#405](https://github.com/CrowdStrike/falcon-mcp/issues/405)
* **modules/correlation-rules:** add NG-SIEM Correlation Rules module ([#391](https://github.com/CrowdStrike/falcon-mcp/issues/391)) ([afd0a88](https://github.com/CrowdStrike/falcon-mcp/commit/afd0a885238dd75823066aeb4fd6dc82f501d218))
* **modules/data-protection:** add Data Protection module ([#428](https://github.com/CrowdStrike/falcon-mcp/issues/428)) ([fff356c](https://github.com/CrowdStrike/falcon-mcp/commit/fff356ca32558be20cdd36488f718aaf1eb65262))
* **modules/quarantine:** add quarantine workflows ([#352](https://github.com/CrowdStrike/falcon-mcp/issues/352)) ([0e66344](https://github.com/CrowdStrike/falcon-mcp/commit/0e66344356eca035b2fb2e53a2a5e6f3eab5c6b5))
* **modules/rtr:** add audit and command wait workflows ([#356](https://github.com/CrowdStrike/falcon-mcp/issues/356)) ([14b1007](https://github.com/CrowdStrike/falcon-mcp/commit/14b1007acfa655a01b05ee1a5fc6a78cc56531ba))


### Bug Fixes

* **docker:** use multi-stage COPY pattern for uv binary ([#411](https://github.com/CrowdStrike/falcon-mcp/issues/411)) ([a1f0628](https://github.com/CrowdStrike/falcon-mcp/commit/a1f062873ec0e8906ee665a7035e921b8ed05142))
* **modules/cloud:** return int count from count_kubernetes_containers ([#397](https://github.com/CrowdStrike/falcon-mcp/issues/397)) ([42d1172](https://github.com/CrowdStrike/falcon-mcp/commit/42d1172aea7ddbebbe8c9ba86dd106c3e8c58cf7))
* **modules/correlation-rules:** align API fields with live behavior ([#407](https://github.com/CrowdStrike/falcon-mcp/issues/407)) ([0199222](https://github.com/CrowdStrike/falcon-mcp/commit/019922262303dfd43398879ea82e7e5ee9620455))
* **modules/idp:** resolve FieldInfo defaults before building search_criteria ([#396](https://github.com/CrowdStrike/falcon-mcp/issues/396)) ([47205d1](https://github.com/CrowdStrike/falcon-mcp/commit/47205d12b6d74227139bf99c4e935e4e0b60dffa))
* **modules/intel:** parse JSON format in get_mitre_report ([#429](https://github.com/CrowdStrike/falcon-mcp/issues/429)) ([62e698c](https://github.com/CrowdStrike/falcon-mcp/commit/62e698ccbff38f384a6cd76b3a93dfa2dc648da9)), closes [#383](https://github.com/CrowdStrike/falcon-mcp/issues/383)

## [0.10.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.9.0...v0.10.0) (2026-05-18)


### Features

* **modules/cases:** add Case Management module ([#388](https://github.com/CrowdStrike/falcon-mcp/issues/388)) ([58d8460](https://github.com/CrowdStrike/falcon-mcp/commit/58d84606368fdff82eb5415388c45c56e654c35d))
* **modules/cloud:** add CSPM findings query and suppression tools ([#378](https://github.com/CrowdStrike/falcon-mcp/issues/378)) ([c76dce5](https://github.com/CrowdStrike/falcon-mcp/commit/c76dce55ef634a5cf33cb56d084546aaf99d4887))
* **modules/shield:** add Falcon Shield (SaaS Security) module ([#355](https://github.com/CrowdStrike/falcon-mcp/issues/355)) ([3218176](https://github.com/CrowdStrike/falcon-mcp/commit/3218176eb356f3dc6d4125f467d8b1b376b36051))
* **modules:** remove deprecated incidents module ([#368](https://github.com/CrowdStrike/falcon-mcp/issues/368)) ([54c4948](https://github.com/CrowdStrike/falcon-mcp/commit/54c494838106e93691c4b1c22c85fc7a2a92de79)), closes [#330](https://github.com/CrowdStrike/falcon-mcp/issues/330)
* publish falcon mcp to the mcp registry ([#357](https://github.com/CrowdStrike/falcon-mcp/issues/357)) ([47acb05](https://github.com/CrowdStrike/falcon-mcp/commit/47acb0503f3ad875ea7076cd4f393dcdefb16b5c))


### Bug Fixes

* **server:** falcon_check_connectivity will try auth once before reporting no connectivity to Falcon API ([#363](https://github.com/CrowdStrike/falcon-mcp/issues/363)) ([cea77ef](https://github.com/CrowdStrike/falcon-mcp/commit/cea77ef2f30f9f3339337df8fe69535868c99368))
* **server:** surface diagnostic details on auth failure at startup ([#379](https://github.com/CrowdStrike/falcon-mcp/issues/379)) ([50a8c95](https://github.com/CrowdStrike/falcon-mcp/commit/50a8c95a1dc67e1ef78dfb9cb8f67a151a23686c)), closes [#351](https://github.com/CrowdStrike/falcon-mcp/issues/351)
* **tests:** make NGSIEM async tests actually execute ([#381](https://github.com/CrowdStrike/falcon-mcp/issues/381)) ([64ecd27](https://github.com/CrowdStrike/falcon-mcp/commit/64ecd27e4a8359da2f2dcd93619d86d56dba2343)), closes [#375](https://github.com/CrowdStrike/falcon-mcp/issues/375)
* **tools:** omit outputSchema from tools/list to fit client context budgets ([#376](https://github.com/CrowdStrike/falcon-mcp/issues/376)) ([943fe55](https://github.com/CrowdStrike/falcon-mcp/commit/943fe55952fa023a017ec769d237989d957f5740))


### Refactoring

* **modules:** standardize tool descriptions across all modules ([#385](https://github.com/CrowdStrike/falcon-mcp/issues/385)) ([939d62e](https://github.com/CrowdStrike/falcon-mcp/commit/939d62e4beaa8226d2b3e0ddcf4e8444b65abbab)), closes [#380](https://github.com/CrowdStrike/falcon-mcp/issues/380)

## [0.9.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.8.0...v0.9.0) (2026-04-10)


### Features

* add Flight Control (MSSP) support with member_cid parameter ([#317](https://github.com/CrowdStrike/falcon-mcp/issues/317)) ([d15b1c8](https://github.com/CrowdStrike/falcon-mcp/commit/d15b1c8ea7dcb8739e0a41a6eb9e8f1a823d1973)), closes [#283](https://github.com/CrowdStrike/falcon-mcp/issues/283)
* add version reporting via startup log, CLI flag, and MCP metadata ([#334](https://github.com/CrowdStrike/falcon-mcp/issues/334)) ([27acc45](https://github.com/CrowdStrike/falcon-mcp/commit/27acc450109ea447330d61985656f6d91137dfc4))
* **modules/cloud:** add CSPM asset inventory search ([#319](https://github.com/CrowdStrike/falcon-mcp/issues/319)) ([cbf2614](https://github.com/CrowdStrike/falcon-mcp/commit/cbf2614cc75a550f20170fef97b99e2d992ac50e))
* **modules/rtr:** add real time response support ([#327](https://github.com/CrowdStrike/falcon-mcp/issues/327)) ([d975534](https://github.com/CrowdStrike/falcon-mcp/commit/d975534ff7027d40744d51f3b5594641dbad7b80))


### Bug Fixes

* **modules/cloud:** correct CSPM asset FQL tag filter syntax ([#320](https://github.com/CrowdStrike/falcon-mcp/issues/320)) ([95fd9bd](https://github.com/CrowdStrike/falcon-mcp/commit/95fd9bd1b086b67f0c6b5c92f18334df24034d83))

## [0.8.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.7.0...v0.8.0) (2026-03-09)


### Features

* **modules:** add Custom IOA behavioral rules module ([#307](https://github.com/CrowdStrike/falcon-mcp/issues/307)) ([1c10c1d](https://github.com/CrowdStrike/falcon-mcp/commit/1c10c1d113101f1f596663be90ca067af89407b2))
* **modules:** add firewall management module and tests ([#306](https://github.com/CrowdStrike/falcon-mcp/issues/306)) ([eedd89c](https://github.com/CrowdStrike/falcon-mcp/commit/eedd89ce4aa11db1012143e76b4acd1135d8d4a6))
* **modules:** add MCP tool annotations for all tools ([#303](https://github.com/CrowdStrike/falcon-mcp/issues/303)) ([339e7c4](https://github.com/CrowdStrike/falcon-mcp/commit/339e7c4b723bed7b5759a9f9a5c2ae07d2094d5b)), closes [#229](https://github.com/CrowdStrike/falcon-mcp/issues/229)


### Bug Fixes

* handle trailing-slash redirects and json-rpc content-type in HTTP transports ([#308](https://github.com/CrowdStrike/falcon-mcp/issues/308)) ([b4260b7](https://github.com/CrowdStrike/falcon-mcp/commit/b4260b7c862c0e98e5683f0b1d5f643e63f43e14))


### Refactoring

* **examples/adk:** simplify agent.py and clean up documentation ([#304](https://github.com/CrowdStrike/falcon-mcp/issues/304)) ([4baef37](https://github.com/CrowdStrike/falcon-mcp/commit/4baef37686abe74595f10dc08358de7030baa67b))

## [0.7.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.6.0...v0.7.0) (2026-02-26)


### Features

* **ioc:** add IOC Service Collection search/create/delete module ([#292](https://github.com/CrowdStrike/falcon-mcp/issues/292)) ([ef1b502](https://github.com/CrowdStrike/falcon-mcp/commit/ef1b502e17efb9065777d2f9dcf2014866013a70))
* **server:** pass host/port to FastMCP to prevent HTTP 421 in proxied deployments ([#293](https://github.com/CrowdStrike/falcon-mcp/issues/293)) ([7aff692](https://github.com/CrowdStrike/falcon-mcp/commit/7aff69254f6e505d8b7449108ebf8f02bdeece86)), closes [#291](https://github.com/CrowdStrike/falcon-mcp/issues/291)

## [0.6.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.5.0...v0.6.0) (2026-02-09)


### Features

* **modules/ngsiem:** add NGSIEM module for Next-Gen SIEM search ([#281](https://github.com/CrowdStrike/falcon-mcp/issues/281)) ([00b8385](https://github.com/CrowdStrike/falcon-mcp/commit/00b8385b9c5a404a97fff1a4544a7dc91706b213))

## [0.5.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.4.1...v0.5.0) (2026-02-02)


### Features

* add x-api-key authentication for HTTP transports ([#269](https://github.com/CrowdStrike/falcon-mcp/issues/269)) ([82a594f](https://github.com/CrowdStrike/falcon-mcp/commit/82a594f74fe1359a8585132052c15334f6536f28))
* **modules/detections:** improve FQL filter UX and tool descriptions ([#259](https://github.com/CrowdStrike/falcon-mcp/issues/259)) ([80f0639](https://github.com/CrowdStrike/falcon-mcp/commit/80f0639a30b2c34c41559b4af36884824b5217ba))
* **modules/scheduled-reports:** add scheduled reports and executions module ([#252](https://github.com/CrowdStrike/falcon-mcp/issues/252)) ([8b54b7f](https://github.com/CrowdStrike/falcon-mcp/commit/8b54b7fa2a5f8ab81566e5b58049c66812bcd895))
* **tests:** add integration tests with real API calls ([#263](https://github.com/CrowdStrike/falcon-mcp/issues/263)) ([01b8c97](https://github.com/CrowdStrike/falcon-mcp/commit/01b8c97a432e83e13467e3664518cdb6a7da8a71))


### Bug Fixes

* **modules/scheduled-reports:** return full details from search tools ([#254](https://github.com/CrowdStrike/falcon-mcp/issues/254)) ([c6c39ba](https://github.com/CrowdStrike/falcon-mcp/commit/c6c39babdb701e267b14d598b4e2ebd575475125))
* sync gemini-extension.json version and remove harden-runner ([#274](https://github.com/CrowdStrike/falcon-mcp/issues/274)) ([e152edb](https://github.com/CrowdStrike/falcon-mcp/commit/e152edb4edc35895ddebc5e53b27127f0adbff55))

## [0.4.1](https://github.com/CrowdStrike/falcon-mcp/compare/v0.4.0...v0.4.1) (2026-01-08)


### Bug Fixes

* **docs:** updated docs but more for testing release pipeline ([c7106f9](https://github.com/CrowdStrike/falcon-mcp/commit/c7106f9632112eeccb77ac4a18b7620c113fd143))

## [0.4.0](https://github.com/CrowdStrike/falcon-mcp/compare/v0.3.0...v0.4.0) (2026-01-08)


### Features

* **client:** allow credential setting through __init__ parameters ([#245](https://github.com/CrowdStrike/falcon-mcp/issues/245)) ([120e56f](https://github.com/CrowdStrike/falcon-mcp/commit/120e56ffc8640535694dc162f08fa9d9d97efc65))
* **modules/intel:** provide the ability to get the mitre report in json or csv format ([#227](https://github.com/CrowdStrike/falcon-mcp/issues/227)) ([04e4411](https://github.com/CrowdStrike/falcon-mcp/commit/04e441121e86b5468f7abaa4a7e644d58ddda8ee))
* **server:** add stateless HTTP mode for scalable deployments ([#242](https://github.com/CrowdStrike/falcon-mcp/issues/242)) ([8c39de1](https://github.com/CrowdStrike/falcon-mcp/commit/8c39de1035e07fd0827d643ca21901b1ad213b6b))


### Bug Fixes

* **tests/intel:** correct test expectations for get_mitre_report ([#241](https://github.com/CrowdStrike/falcon-mcp/issues/241)) ([c1e8b6b](https://github.com/CrowdStrike/falcon-mcp/commit/c1e8b6bc18e53f29fdc6b553ada1c7cda9bde0b6))


### Refactoring

* reduce repeated API code patterns in modules ([2d5debd](https://github.com/CrowdStrike/falcon-mcp/commit/2d5debd6264dc7db9796085f25b8ec10d616cbbe))
* **utils:** simplify generate_md_table function ([#214](https://github.com/CrowdStrike/falcon-mcp/issues/214)) ([792e128](https://github.com/CrowdStrike/falcon-mcp/commit/792e128315c65cdc1d82586a168a71082cec869b))

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
