import subprocess
import sys
import logging
import re
import os
import json
from collections import defaultdict
from glob import iglob

#3d-party libs
import jmespath
import hcl

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

EXPECTED_CLI_ARG_COUNT = 2

def include_el(el):
    """
    Determine whether to include specified input element in output by filtering for dups etc.

    Return: True if element should be included

    Assumptions:
      x Input file is comprised of only like resources (e.g., only ec2)
    """

    #check: ensure tag Name same as resource name
    unique_names = defaultdict()

    main_name = el[0]
    list_el = el[1]
    tag_name = jmespath.search("tags.Name", list_el)

    if tag_name != None:
        main_name_clean = re.sub("[^a-z]", "", main_name, 0, re.IGNORECASE)
        name_tag_clean = re.sub("[^a-z]", "", tag_name, 0, re.IGNORECASE)
        if main_name_clean != name_tag_clean:
            raise Exception("Resource name '" + main_name + "' did not match tag Name '" + tag_name + "'")

    #filter: Don’t allow dup names for a given resource
    if main_name in unique_names:
        log.info("excluding dup resource name: " + main_name)
        return False
    else:
        unique_names[main_name] = el

    #TODO filter: tag processing to separate tf folders
    return True

def process_tf_file(in_fname, out_dir):
    with open(in_fname, 'r', encoding='utf-8') as f:
        data = hcl.load(f)

    app_dir = os.path.dirname(os.path.realpath(__file__))

    #Determine out_data resource structure
    out_data = defaultdict()
    out_data["resource"] = defaultdict()
    out_data_type = out_data["resource"]

    #Assign resource type in output
    in_data_type = None
    if "resource" in data:
        for el in data["resource"].items():
            in_data_type_name = el[0]
            out_data_type[in_data_type_name] = defaultdict()
            out_data_type = out_data_type[in_data_type_name]
            in_data_type = el[1]
            break

    #Iterate each input resource, determine if to include / modify in output
    if not in_data_type is None:
        for el in in_data_type.items():
            if include_el(el):
                out_data_type[el[0]] = el[1]
    else:
        #Is non-resource file like provider or variables - pass through as-is
        out_data = data

    out_file = os.path.join(out_dir, os.path.basename(in_fname))
    temp_file = out_file + ".tmp"
    with open(temp_file, "w", encoding='utf-8') as f:
        json.dump(out_data, f, indent=4)

    subprocess.check_call([os.path.join(app_dir, "run-json2hcl.sh"), temp_file, out_file])
    os.remove(temp_file)

def main():
    """
    usage: terraforming-filter in-dir out-dir

    Convert all *.tf files in specified input folder to filtered *.tf files in target output folder
    """

    if len(sys.argv) - 1 != EXPECTED_CLI_ARG_COUNT:
        raise ValueError("usage: in-dir out-dir")

    in_dir = os.path.abspath(sys.argv[1])
    out_dir = os.path.abspath(sys.argv[2])

    iterator = iglob(os.path.join(in_dir, '*.tf'))
    for in_fname in iterator:
        process_tf_file(in_fname, out_dir)

main()
