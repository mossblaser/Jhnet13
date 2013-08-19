import os

import web

import deslash
import static
import publication
import error

from mako.template import Template
from mako.lookup   import TemplateLookup

def rel_path(path):
	"""
	Convert a path relative to this file to an absolute path
	"""
	return os.path.join(os.path.dirname(__file__), path)

def site_path(path):
	"""
	Convert a path relative to the web directory specified by the JHNET_DIR
	environment variable to an absolute path. Defaults the the parent directory if
	not defined.
	"""
	return os.path.join(os.environ.get( "JHNET_DIR"
	                                  , os.path.join(os.path.dirname(__file__),".."))
	                   , path)

################################################################################
# URL Decoding
################################################################################

# Alternating url_regex, handler_class_name strings
urls = [
	# The primary website sections
	"/",                       "index",
	"/about",                  "about",
	"/projects/figures(/.*|)", "figures",
	"/projects(/.*|)",         "projects",
	"/articles(/.*|)",         "articles",
	"/misc(/.*|)",             "misc",
	
	# Static resources live in these directories
	"(/(?:img|css|js)/.*)", "static_resources",
	
	# If in doubt, remove trailing slashes
	"/(.*/)", "deslash.Deslash",
]


################################################################################
# Load templates
################################################################################

template_lookup = TemplateLookup(directories = [site_path("templates")])

index_template          = template_lookup.get_template("index.mako")
about_template          = template_lookup.get_template("about.mako")
pub_listing_template    = template_lookup.get_template("pub_listing.mako")
pub_template            = template_lookup.get_template("pub.mako")
misc_template           = template_lookup.get_template("dirlist.mako")
notfound_template       = template_lookup.get_template("notfound.mako")
internal_error_template = template_lookup.get_template("internalerror.mako")

################################################################################
# Define menu
################################################################################

# List of (menu_text, menu_url, homepage_menu_class) tuples
site_menu = [
	("About Me", "/about",    "home-buttons-about"),
	("Projects", "/projects", "home-buttons-projects"),
	("Articles", "/articles", "home-buttons-articles"),
	("/misc",    "/misc/",    "home-buttons-misc"),
]


################################################################################
# Define Page Handlers
################################################################################

# The homepage: Just a static page from a template
index = static.StaticTemplate( index_template
                             , root_path = "/"
                             , site_menu = site_menu
                             )


# About page: just a static page from template
about = static.StaticTemplate( about_template
                             , root_path = "/"
                             , site_menu = site_menu
                             , site_menu_active_name = "About Me"
                             , title = "About Me"
                             )

# Figure repository, based on the publications system
figures = publication.Publications( "/projects/figures"
                                  , site_path("figures")
                                  , "Figures"
                                  , pub_listing_template
                                  , pub_template
                                  , site_menu = site_menu
                                  , site_menu_active_name = "Projects"
                                  , root_path = "/"
                                  )

# Project pages, based on the publications system
projects = publication.Publications( "/projects"
                                   , site_path("projects")
                                   , "Projects"
                                   , pub_listing_template
                                   , pub_template
                                   , site_menu = site_menu
                                   , site_menu_active_name = "Projects"
                                   , root_path = "/"
                                   )

# Articles, based on the publications system
articles = publication.Publications( "/articles"
                                   , site_path("articles")
                                   , "Articles"
                                   , pub_listing_template
                                   , pub_template
                                   , site_menu = site_menu
                                   , site_menu_active_name = "Articles"
                                   , root_path = "/"
                                   )

# The misc directory (with directory browser)
misc = static.StaticBrowseableDir( "/misc"
                                 , site_path("misc")
                                 , misc_template
                                 , root_path = "/"
                                 , site_menu = site_menu
                                 , site_menu_active_name = "/misc"
                                 )

# Static bits just taken from the static directory
static_resources = static.StaticDir("/", site_path("static"))

notfound_handler = error.NotFound( notfound_template
                                 , root_path = "/"
                                 , site_menu = site_menu
                                 , site_menu_active_name = None
                                 )

internal_error_handler = error.InternalError( internal_error_template
                                            , root_path = "/"
                                            , site_menu = site_menu
                                            , site_menu_active_name = None
                                            )

# Set up the application
app = web.application(urls, globals())
app.notfound = notfound_handler

if __name__ == "__main__":
	# If running standalone, boot up the testing server
	app.run()
else:
	# If running via FCGI then this is probably production, show sanitised errors
	app.internalerror = internal_error_handler
