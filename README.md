# ArchiveStyle for BookGen

This repository contains a [BookGen](https://github.com/marrus-sh/BookGen) style which can effectively be used as a static site generator to create pages which are similar to those of [Archive of our Own](https://archiveofourown.org/) from a Markdown, per-chapter source.

## Usage

BookGen has a number of configuration options; this guide is targeted at the beginner and only covers the basics.
You will need some command-line knowledge to follow this guide.

### Prerequisites:

BookGen has a number of prerequisites; as ArchiveStyle only targets HTML output, you will only need the following installed on your computer:

+ GNU Make, version 3.81 or later. You can see which version of `make` is installed on your computer using `make -v`. If you need, you can download a new version of `make` here: <https://www.gnu.org/software/make/>.

+ Pandoc.
Installation instructions can be found here: <https://pandoc.org/installing.html>.
You only need to install `pandoc-citeproc` if you are creating a work with a bibliography.

+ Python 3.
You can use `python3 -V` to see if you already have Python installed on your computer.

+ Panflute.
This is a Python library used to create the BookGen Pandoc filters.
You can install it with `pip3 install panflute`.

+ Zip.
It is probably already installed on your computer (you can use `zip -v` to check), but if you need it, you can get it here: <http://infozip.sourceforge.net/Zip.html>.

+ Git.
You do not *technically* need Git installed on your computer; you can just download the repositories manually and place them in the proper locations.
However, using Git makes it easier to keep things up-to-date, and handles submodule dependencies for you.
You can check the version you have installed using `git --version`, and download the latest version at <https://www.git-scm.com/downloads>.

Of the above, Pandoc and Panflute are the most likely things you will have to install yourself.

### Installation:

First, open a command line and `cd` into the parent directory within which you will place your source.
You have two options for installation:

1. If you are going to be tracking this entire directory with `git` (and not just using it to keep modules up to date), then make sure it is initialized (run `git init`) and then you will use `git submodule add`.

2. Otherwise, you will use `git clone`.

In the commands below, replace `$INSTALL` with `git submodule add` or `git clone` as determined above.

To install BookGen itself:

	$INSTALL https://github.com/marrus-sh/BookGen.git Modules/BookGen

To install ArchiveStyle:

	$INSTALL https://github.com/marrus-sh/ArchiveStyle.git Modules/ArchiveStyle

Next, download the submodules required by BookGen with the following command:

	git submodule update --recursive --init

Finally, create a `Makefile` (that is, a plain-text file literally named `Makefile`) in your source directory with the following contents:

```make
SHELL = /bin/sh
BOOKGEN :=  Modules/BookGen
ARCHIVESTYLE := Modules/ArchiveStyle

# Uncomment these lines if you want to use multiple drafts (see below):
# DRAFTS := Drafts
# export DRAFTS

default: html
bookgen: ; @$(MAKE) -ef "$(BOOKGEN)/GNUmakefile"
archivestyle: ; @$(MAKE) -f "$(ARCHIVESTYLE)/Makefile"
Makefile: ;
%: archivestyle; @$(MAKE) -ef "$(BOOKGEN)/GNUmakefile" $@
clobber distclean gone:
	@$(MAKE) -f "$(ARCHIVESTYLE)/Makefile" gone
	@$(MAKE) -ef "$(BOOKGEN)/GNUmakefile" gone
.PHONY: default bookgen archivestyle clobber distclean gone
```

This looks complicated, but it is just setting things up to defer any `make` commands you make to BookGen and/or ArchiveStyle as required.

### Setup:

Create a file titled `info.yml` in your source directory.
This is a [YAML](https://yaml.org/) file which will store all of your metadata for your work.
The values supported by ArchiveStyle are:

```yaml
# Please only use plaintext for these properties:
title: "Work title"
series: "Work series"
author: "Your name"
publisher: "Your publisher/website"
description: "Work summary"
homepage: "https://example.com/The-homepage-for-your-work" # A URL
year: "The copyright year(s) of your work"
rights: "A short rights statement about your work"
draft: "1" # The draft number of the work (this will be added automatically if you are in drafts mode)
lang: "en" # Work language as an IETF (i.e., HTML) langauge tag
final: true # If this is a final, published draft; adds copyright declaration

# You can use lists and HTML in the following properties:
ArchiveStyle:
  metadata:
    rating: "The rating of your work (e.g., Mature)"
    warning: "Any content warnings for your work"
    category: "F/F, Other, etc."
    fandom: "Fandom name(s)"
    relationship: "Relationship pairings"
    character: "Characters in the fic"
    tagged: "Additional tags"
  clickthrough: |
    If set, this adds a clickthrough disclaimer for viewing the content.
  summary: |
    Work summary (with HTML).
  foreword: |
    Leading work notes
  afterword: |
    Trailing work notes
```

You needn't specify all (or any) of the above, but an empty `info.yml` file *will* be created if you do not make one.
You can also set these values on a per-chapter basis using YAML frontmatter.

### Writing your book:

Your book can consist of any number of frontmatter chapters, main chapters, and appendices.
These must all be placed in a folder titled `Markdown` in your source directory, and must have an extension of `.md`.
**Do not use colons, semicolons, or spaces in filenames** as Makefiles are not well-equipped to handle these characters and everything might break.

The type of a chapter is determined by its location:

+ All files directly in the `Markdown` directory are frontmatter, ordered alphabetically.
You can use leading digits to manually determine their order.

+ All files in the `Markdown/Chapters` directory with a filename of two digits are chapters.
The chapter number is given by the filename.

+ All files in the `Markdown/Chapters` directory with a filename of `A`, followed by two digits (for example, `A01`) are appendices.
The appendix number is given by the filename.

Alternatively, if you set `DRAFTS := Drafts` in your Makefile above, you may instead give your chapters as *folders* of Markdown files in the `Drafts` directory, and the alphabetically last file in each will be automatically linked into the `Markdown` directory for you.
(For example, the file at `Drafts/Chapter/01/Draft_02.md` will be linked from `Markdown/Chapter/01.md`.)
This allows you to store multiple drafts of a chapter alongside one another, with the last draft used as the final result.

### Markdown syntax:

BookGen uses Pandoc under the hood, so the Markdown syntax is [Pandoc Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown).

### Compiling your book:

To compile your book, simply run `make -s`.
This will create two new directories: `HTML/Archive`, which will contain the compiled HTML files (which you can then serve on your website) and `Zip`, which will contain ZIPs of the compiled files and source.
If you don't need the zips, run `make -s NOARCHIVE=1`

`make gone` will delete all directories created by BookGen and all their contents.
If you are in drafts mode, **it will also delete the `Markdown` directory**, so be sure to store all your files as drafts if you plan on making use of this feature.

### Customization:

You can of course customize the stylesheet by editing the file at `Modules/ArchiveStyle/Archive.css`.
Or, you can make your own additional stylesheets in the `Modules/ArchiveStyle` directory.
**If you make a new stylesheet, also copy and rename `Archive.py` to match its filename.**
Otherwise, the chapter metadata will not be inserted into your files.

### Updating:

To update, just `cd` the `Modules/BookGen` and/or `Modules/ArchiveStyle` directory and `git pull --recurse-submodules`.
