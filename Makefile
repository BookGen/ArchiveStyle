# Creates links from `$srcdir/*.c[ls]s` to `Styles/*.c[ls]s`.
# Also links associated python filters.
#
# Example usage from within another Makefile:
#
# 	archivestyle: ; $(MAKE) -f ArchiveStyle/Makefile
# 	.PHONY: archivestyle

SHELL = /bin/sh
srcdir := $(patsubst %/Makefile,%,$(lastword $(MAKEFILE_LIST)))
archivesrcs := $(wildcard $(srcdir)/*.c[ls]s)
archivepys := $(foreach src,$(sort $(basename $(archivesrcs))),$(wildcard $(patsubst %,%.py,$(src))))
archivestyles := $(patsubst $(srcdir)/%,Styles/%,$(archivesrcs) $(archivepys))

archive: $(archivestyles);
$(archivestyles): Styles/%: $(srcdir)/%
	[[ -d Styles ]] || mkdir Styles
	ln -fs "$(realpath $<)" $@
clobber distclean gone: ; rm -f $(archivestyles)
.PHONY: archive clobber distclean gone
