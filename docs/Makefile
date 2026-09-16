# Minimal Sphinx makefile for the discretus documentation.

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help html dirhtml latexpdf linkcheck doctest coverage strict serve clean Makefile

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "Additional targets provided by this file:"
	@echo "  strict    build HTML with warnings treated as errors"
	@echo "  serve     build HTML and serve it on http://localhost:8000"

# Builders passed straight through to Sphinx.
html dirhtml latexpdf linkcheck doctest coverage:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# The invocation the release check uses. The keep going flag reports every
# warning instead of stopping at the first one.
strict:
	@$(SPHINXBUILD) -b html -W --keep-going "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

serve: html
	@echo "Serving the documentation on http://localhost:8000"
	@python -m http.server 8000 --directory "$(BUILDDIR)/html"

clean:
	@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
