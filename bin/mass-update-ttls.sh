#!/usr/bin/env bash

_red="\e[0;31m"
_b_red="\e[1;31m"
_nocolor="\e[0m"

error() {
    echo "ERROR: $@" >&2
    usage
    exit 1
}

usage() {
    echo "Usage: $0 [-h] { -t <ttl> | -f <filter> | --do-update } <zone>" >&2
    echo "   -h / --help:        show this message" >&2
    echo "   -f / --filter:      filter the list of domains by this string" >&2
    echo "   -t / --ttl:         The ttl to set" >&2
    echo "   --do-update:        Do the ttl updates instead of just printing htem" >&2
    echo "   zone:               The zone to operate on" >&2
}

zone=""
filter=""
ttl=500
do=""
while [ $# -ne 0 ]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -f|--filter)
            shift; [ $# -ge 1 ] || error "Missing arugment for -f/--filter"
            filter="$1"; shift
            ;;
        -t|--ttl)
            shift; [ $# -ge 1 ] || error "Missing argument for -t/--ttl"
            ttl="$1"; shift
            ;;
        --do-update)
            shift; do="YES";
            ;;
        -*)
            error "Invalid parameter: $1"
            ;;
        *)
            [ -z "${zone}" ] || error "More than one zone given"
            zone="$1"; shift
            ;;
    esac
done
if [ -z "${zone}" ]; then
    error "You must supply a zone to operate on"
fi
domains="$(./pdns show-rrsets $zone | awk '{ print $1" "$4" "$5}')"
if [ ! -z "${filter}" ]; then
    domains="$(echo "$domains" | grep $filter)"
fi
#don't include non CNAME/ALIAS/A/AAAA domains 
domains="$(echo "$domains" | grep -v "TXT" | grep -v "MX" | grep -v "SOA" | grep -v "NS")"
while read -r line; do
    echo "./pdns edit-rrset --ttl $ttl --replace $zone $line";
    if [ ! -z "${do}" ]; then
        ./pdns edit-rrset --ttl $ttl --replace $zone $line
    fi;
done <<< "$domains"
exit ${rc}
