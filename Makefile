# Creates links from `$srcdir/*.c[ls]s` to `Styles/*.c[ls]s`.
#
# Example usage from within another Makefile:
#
# 	archivestyle: ; $(MAKE) -f ArchiveStyle/Makefile
# 	.PHONY: archivestyle

SHELL = /bin/sh
srcdir := $(patsubst %/Makefile,%,$(lastword $(MAKEFILE_LIST)))
archivesrcs := $(wildcard $(srcdir)/*.c[ls]s)
archivestyles := $(patsubst $(srcdir)/%,Styles/%,$(archivesrcs))

archive: $(archivestyles);
$(archivestyles): Styles/%: $(srcdir)/%
	[[ -d Styles ]] || mkdir Styles
	ln -fs "$(realpath $<)" $@
clobber distclean gone: ; rm -f $(archivestyles)
.PHONY: archive clobber distclean gone
