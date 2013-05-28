import web

import deslash
import static
import publication
import error

from mako.template import Template
from mako.lookup   import TemplateLookup

################################################################################
# URL Decoding
################################################################################

# Alternating url_regex, handler_class_name strings
urls = [
	# The primary website sections
	"/",               "index",
	"/about",          "about",
	"/projects(/.*|)", "projects",
	"/articles(/.*|)", "articles",
	"/misc(/.*|)",     "misc",
	
	# Static resources live in these directories
	"(/(?:img|css|js)/.*)", "static_resources",
	
	# If in doubt, remove trailing slashes
	"/(.*/)", "deslash.Deslash",
]


################################################################################
# Load templates
################################################################################

template_lookup = TemplateLookup(directories = ["./templates"])

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

# Project pages, based on the publications system
projects = publication.Publications( "/projects"
                                   , "./projects"
                                   , "Projects"
                                   , pub_listing_template
                                   , pub_template
                                   , site_menu = site_menu
                                   , site_menu_active_name = "Projects"
                                   , root_path = "/"
                                   )

# Articles, based on the publications system
articles = publication.Publications( "/articles"
                                   , "./articles"
                                   , "Articles"
                                   , pub_listing_template
                                   , pub_template
                                   , site_menu = site_menu
                                   , site_menu_active_name = "Articles"
                                   , root_path = "/"
                                   )

# The misc directory (with directory browser)
misc = static.StaticBrowseableDir( "/misc"
                                 , "./misc"
                                 , misc_template
                                 , root_path = "/"
                                 , site_menu = site_menu
                                 , site_menu_active_name = "/misc"
                                 )

# Static bits just taken from the static directory
static_resources = static.StaticDir("/", "./static")

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


if __name__ == "__main__":
	app = web.application(urls, globals())
	app.notfound = notfound_handler
	app.internalerror = internal_error_handler
	app.run()
