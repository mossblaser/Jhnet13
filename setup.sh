#!/bin/bash

# A quick hack of a script which sets up the current working directory as a
# Jhnet site root.

REPO_DIR="$(realpath "$(dirname "$0")")"

# Link in jhnet main script and htaccess
ln -s "$REPO_DIR/jhnet.py" jhnet.py
ln -s "$REPO_DIR/root_htaccess" .htaccess

# Link in site content directories
ln -s "$REPO_DIR/templates" templates
ln -s "$REPO_DIR/static"    static

# Make key directories for site content
mkdir articles projects misc

# Link accross READMEs
ln -s "$REPO_DIR/articles/README.html" "articles/README.html"
ln -s "$REPO_DIR/projects/README.html" "projects/README.html"
ln -s "$REPO_DIR/misc/README.html"     "misc/README.html"

# If not already got ToCs, create them
[ -f "articles/toc.json" ] || (echo "[]" > "articles/toc.json")
[ -f "projects/toc.json" ] || (echo "[]" > "projects/toc.json")

# Set up environment for server
virtualenv --distribute .

# Add environment variables (massive hack)
echo 'sys.path.append("'"$REPO_DIR"'")'                >> lib/python*/site.py
echo 'os.environ["JHNET_DIR"]="'$(realpath "`pwd`")'"' >> lib/python*/site.py

# Activate the virtualenv
source bin/activate

pip install web.py
pip install mako
pip install flup

deactivate

echo "Done!"
