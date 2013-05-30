#!/usr/bin/env python

"""
Shared utilities for the publication tools.
"""

def unique(base_name, taken_names):
	"""
	Returns base_name or base_name prefixed with "%d_" which ensures it does not
	appear in taken_names.
	"""
	given_name = base_name
	cnt = 1
	while given_name in taken_names:
		given_name = "%d_%s"%(cnt, base_name)
		cnt += 1
	return given_name

