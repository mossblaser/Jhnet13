#!/usr/bin/env python

"""
Takes a publication directory toc.json and an article's *.meta file and merges
the two.
"""

import sys
import json

if __name__=="__main__":
	toc_json_file_name = sys.argv[1]
	meta_file_name     = sys.argv[2]
	
	toc_json = json.load(open(toc_json_file_name,"r"))
	meta     = json.load(open(meta_file_name,"r"))
	
	# Remove existing copies of the metadata
	for pub in toc_json:
		if pub["url"] == meta["url"]:
			toc_json.remove(pub)
			break
	
	# Add the meta-data
	toc_json.append(meta)
	
	# Write back to the toc
	json.dump(toc_json, open(toc_json_file_name,"w"))
