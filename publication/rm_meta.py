#!/usr/bin/env python

"""
Takes a publication directory toc.json and an article's URL and removes the
article with that URL
"""

import sys
import json

if __name__=="__main__":
	toc_json_file_name = sys.argv[1]
	target_url         = sys.argv[2]
	
	toc_json = json.load(open(toc_json_file_name,"r"))
	
	# Remove existing copies of the metadata
	for pub in toc_json:
		if pub["url"] == target_url:
			toc_json.remove(pub)
			break
	
	# Write back to the toc
	json.dump(toc_json, open(toc_json_file_name,"w"))

