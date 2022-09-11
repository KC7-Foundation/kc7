#!/usr/bin/env python

import yaml
import json

with open("vikings.yaml", "r") as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


print(json.dumps(data, indent=3))
