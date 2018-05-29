# PDNS API client

This a PDNS API client implementation in Python.

## Getting started

### Prerequisites

[python-requests](http://docs.python-requests.org/)

### Installing

```
pip install -r requirements.txt
```

## Example usage
Add a www subdomain to the localhost server for the example.org domain, with an A record of 192.0.5.9

NB: the domain should always end with the .
```
./pdns -a user:pass apiurl edit-rrset --add  localhost example.org. www A 192.0.5.9
```
Edit the www subdomain to have a different IP for the A
```
./pdns -a user:pass apiurl edit-rrset --add  localhost example.org. www A 192.0.5.10
```
List RRsets in the example.org zone
```
./pdns -a user:pass apiurl show-rrsets localhost example.org.
```

## Full CLI list
```
usage: pdns [-h] [-a USERNAME:PASSWORD] [-k API_KEY] [-i] url action ...

CLI client for the PowerDNS API

positional arguments:
  url                   PowerDNS API URL

optional arguments:
  -h, --help            show this help message and exit
  -a USERNAME:PASSWORD, --auth USERNAME:PASSWORD
                        credentials for Basic authentication
  -k API_KEY, --api-key API_KEY
                        API key
  -i, --insecure        allow insecure TLS connections

actions:
  action
    list-servers        list servers
    show-server         show details for a server
    add-server          add a new server (pdnscontrol only)
    edit-server         add a new server (pdnscontrol only)
    delete-server       delete a server (pdnscontrol only)
    list-config         list config settings
    list-zones          list zones
    show-zone           show details for a zone
    add-zone            add a new zone, return zone ID
    edit-zone           add a new zone
    delete-zone         delete a zone
    show-rrsets         show Resource Record sets for a zone
    edit-rrset          add/replace/delete a record in Resource Record set
    delete-rrset        delete a Resource Record set
    edit-rrset-comments
                        add/replace/delete a comment in Resource Record set
    notify              send a DNS NOTIFY to all slaves for a zone
    axfr-retrieve       retrieve a zone from the master
    export              export a zone in AXFR format
    check               verify a zone content/configuration
    list-metadata       list all metadata for a zone
    show-metadata       show metadata of a given kind for a zone
    add-metadata        add a new set of metadata for a zone
    edit-metadata       edit a set of metadata for a zone
    delete-metadata     delete all metadata of a given kind for a zone
    list-cryptokeys     list all cryptokeys from a zone
    show-cryptokey      show a cryptokey from a zone
    add-cryptokey       add a new cryptokey to a zone
    edit-cryptokey      edit a cryptokey from a zone
    delete-cryptokey    delete a cryptokey from a zone
    search              search across all zones, records and comments
    search-log          search in the log
    statistics          show internal statistics
    flush-cache         flush the cache for a given domain name
```
## TODO

See [TODO](TODO.md).

## Authors

* **Pierre Guinoiseau** - *Initial work*
