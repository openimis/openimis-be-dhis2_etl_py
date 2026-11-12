# openimis-be-dhis2_etl_py

openIMIS Module to push data into DHIS2


there is 2 methods available, both require to push for the metadata first: 
- ADX : pushd agregated data
- PROGAM :  push trackend entity program


## seting up the module

The module ships **without** a DHIS2 host, credentials or salt: each deployment must set them in
the module configuration (`core.ModuleConfiguration`, module `dhis2_etl`, layer `be`). Until they
are set, a warning is logged at start-up and any push fails with `ImproperlyConfigured` naming the
missing setting.

```
    "dhis2" : {
        "host": "https://dhis2.example.org/",
        "username": "<dhis2 user>",
        "password": "<dhis2 password>"
    },
    "salt": "<deployment-specific secret>",
    "export_names": false
```

- `salt` (required): the secret used to pseudonymise the insuree identifiers exported as the
  `CHFId` and `insuranceId` attributes (`md5(salt + chf_id)`). Use a long random value specific to
  the deployment and keep it secret: anyone knowing it can recompute the hash of a known insurance
  number and re-identify the insuree in DHIS2. Changing it changes every exported identifier, so
  keep it stable once data has been pushed. Deployments that relied on the former built-in default
  (`"LeSalt"`) keep their existing DHIS2 identifiers only by setting that value explicitly, which
  leaves them pseudonymised with a public salt: plan a re-import with a new secret salt instead.
- `export_names` (default `false`): the insuree first and last names (`firstName`, `lastName`
  attributes) are personal data and are not exported unless this is set to `true`.

the full default configuration can be found in the app.py file where DE and program id could be updated

## Pushing metadata

can be done in one command 

`python manage.py pushmetadata 2000-01-01 all`

2000-01-01 is the reference date, it is use to push only newer data, usefull when updating the metadata

or can be done step by step are described below

    #. create or configure a  root orgunit

    `python manage.py pushmetadata 2000-01-01 createRoot`

    (python manage.py pushmetadata startdate enddate createRoot)

    ```
        "location":{
            "rootOrgUnit":"E0FtAX5eNc3",
            "rootOrgUnitName":"DemOpenIMIS",
            "rootOrgUnitCode":"Root",
            "attributes":{
                "locationId":"gMNNTAdZbW1",
                "locationType":"ffZOxd5V2UK"
            }
        },
    ```

    #. create openIMIS orgunit structure

    for the ADX, a function can be specified to do the mapping between the openIMIS orgunit and existing DHIS2 orgunit but this is not supported yet for the program

    `python manage.py pushmetadata 2000-01-01 orgunit`

    #. push the optionset

    this is only usefull for pogram


    `python manage.py pushmetadata 2000-01-01 optionset`

    This  will push optionset
        - gender 
        - profession 
        - groupType 
        - education 
        - product 
        - diagnosis 
        - item
        - service

    they all can be pushed manualy ex :  `python manage.py pushmetadata 2000-01-01 product`


 
## pushing program 

    `python manage.py pushprogram 2000-01-01 all`

    will update the enrolment then the policy, then the claim, then the funding

    each step can be done independently: 

    - `python manage.py pushprogram 2000-01-01 enroll`
    - `python manage.py pushprogram 2000-01-01 insureepolicies`
    - `python manage.py pushprogram 2000-01-01 insureepoliciesclaims`
    - `python manage.py pushprogram 2000-01-01 funding`


    it is also possible to send population data (in village) to DHIS2 witht he command `python manage.py pushprogram 2000-01-01 population`



    This will push data in 3 programs (TBC)
    - Family-insuree [enrollment] Policy [program registration / event]
    - Claims (claim details[program registration / event], Claims Services[event], Claim Items[event])
    - Funding (claim details[program registration / event], Claims Services[event], Claim Items[event])




## pushing ADX

    adx requires specific metadata definition that can be created automatically with 

    `python manage.py pushadx 2000-01-01 pushMetadata`


    then each month the datasets can be pushed via 


    `python manage.py pushadx 2023-02-01 pushMetadata`

    this code will push data for Jan 23

   
## Scheduled job

in django admin create a job with id `dhis2_adx_monthly_sync`