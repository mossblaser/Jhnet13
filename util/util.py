#!/usr/bin/env python

"""
Shared utilities for the publication tools.
"""

import re
import unicodedata


def slugify(value, separator):
	""" Slugify a string, to make it URL friendly. """
	value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
	value = re.sub('[^\w\s-]', '', value.decode('ascii')).strip().lower()
	return re.sub('[%s\s]+' % separator, separator, value)


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

