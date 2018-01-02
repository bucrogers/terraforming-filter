#!/bin/sh

set -e

json2hcl <"$1" >"$2"
