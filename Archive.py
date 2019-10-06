#!/usr/bin/env python3

"""
Pandoc HTML filters.
"""

from panflute import *
from helper import *
from datetime import datetime, timezone
from collections import OrderedDict
import re

def set_stats(doc):
	doc_text_content = content.text(doc, doc)
	doc.stats['paras'] = int(metadata.text(doc, 'ArchiveStyle.stats.paras', doc.stats['paras']))
	doc.stats['words'] = int(metadata.text(doc, 'ArchiveStyle.stats.words', len(re.split(r'(?<=\S)\s+(?=\S)', re.sub(r'\u2014', ' ', re.sub(r'[\u0021-\u0040\u005B-\u0060\u007B-\u007E\u0080-\u00BF\u00D7\u00F7\u2000-\u2BFF\u2E00-\u2E7F]', '', doc_text_content))))))
	doc.stats['chars'] = int(metadata.text(doc, 'ArchiveStyle.stats.chars', len(doc_text_content)))
	doc.stats['time'] = int(metadata.text(doc, 'ArchiveStyle.stats.time', doc.stats['words'] // 275)) # must be defined after words, obviously

def make_metadata(doc):
	meta = []
	ordered_metadata = OrderedDict([
		('rating', metadata.inlines(doc, 'ArchiveStyle.localization-metadata-rating', 'Rating')),
		('warning', metadata.inlines(doc, 'ArchiveStyle.localization-warning', 'Warnings')),
		('category', metadata.inlines(doc, 'ArchiveStyle.localization-category', 'Categories')),
		('fandom', metadata.inlines(doc, 'ArchiveStyle.localization-fandom', 'Fandoms')),
		('relationship', metadata.inlines(doc, 'ArchiveStyle.localization-relationship', 'Relationship')),
		('character', metadata.inlines(doc, 'ArchiveStyle.localization-character', 'Characters')),
		('tagged', metadata.inlines(doc, 'ArchiveStyle.localization-tagged', 'Additional Tags'))
	])
	metadict = doc.get_metadata('ArchiveStyle.metadata')
	keys = []
	ordered = False
	if isinstance(metadict, dict):
		keys = list(ordered_metadata.keys()) + [x for x in set(metadict.keys()) if not x in ordered_metadata]
	elif isinstance(metadict, list):
		keys = OrderedDict(map(lambda a: tuple(a), metadict)).keys()
		ordered = True
	for path in keys:
		name = ordered_metadata.get(path, metadata.inlines(doc, 'ArchiveStyle.localization-metadata-' + path, path.replace('_', ' ').title()))
		value = doc.get_metadata('ArchiveStyle.metadata', builtin=False).content[next(i for i, v in enumerate(metadict) if v[0] == path)].content[1] if ordered else doc.get_metadata('ArchiveStyle.metadata.' + path, builtin=False)
		if isinstance(value, MetaList):
			meta.append(DefinitionItem(
				[Span(*name, identifier='ArchiveStyle.metadata.' + path)],
				map(lambda item: Definition(*item), map(content.blocks, value.content))
			))
		else:
			item = content.blocks(value)
			if (item):
				meta.append(DefinitionItem(
					[Span(*name, identifier='ArchiveStyle.metadata.' + path)],
					[Definition(*item)]
				))
	if len(meta):
		return DefinitionList(*meta)

def make_stats(doc):
	stats = [
		DefinitionItem([
			Span(*metadata.inlines(doc, 'ArchiveStyle.localization-stats-updated', 'Last update'), identifier='ArchiveStyle.stats.updated')
		], [
			Definition(
				RawBlock('<time datetime="' + doc.stats['updated'].isoformat(timespec='milliseconds') + '">'),
				Plain(Str(doc.stats['updated'].strftime('%Y.%m.%d'))),
				RawBlock('</time>')
			)
		]),
		DefinitionItem([
			Span(*metadata.inlines(doc, 'ArchiveStyle.localization-stats-paras', 'Paragraphs'), identifier='ArchiveStyle.stats.paras')
		], [
			Definition(Plain(Str(format(doc.stats['paras'], ','))))
		]),
		DefinitionItem([
			Span(*metadata.inlines(doc, 'ArchiveStyle.localization-stats-words', 'Words'), identifier='ArchiveStyle.stats.words')
		], [
			Definition(Plain(Str(format(doc.stats['words'], ','))))
		]),
		DefinitionItem([
			Span(*metadata.inlines(doc, 'ArchiveStyle.localization-stats-chars', 'Characters'), identifier='ArchiveStyle.stats.chars')
		], [
			Definition(Plain(Str(format(doc.stats['chars'], ','))))
		]),
		DefinitionItem([
			Span(*metadata.inlines(doc, 'ArchiveStyle.localization-stats-time', 'Minutes to read'), identifier='ArchiveStyle.stats.time')
		], [
			Definition(Plain(Str(u'\u223C' + format(doc.stats['time'], ','))))
		])
	]
	statsdict = doc.get_metadata('ArchiveStyle.stats')
	keys = []
	ordered = False
	orderedstats = ['updated', 'paras', 'words', 'chars', 'time']
	if isinstance(statsdict, dict):
		keys = [x for x in set(statsdict.keys()) if not x in ordered_stats]
	elif isinstance(statsdict, list):
		keys = [x for x in OrderedDict(map(lambda a: tuple(a), metadict)).keys() if not x in ordered_stats]
		ordered = True
	for path in keys:
		name = metadata.inlines('ArchiveStyle.localization-stats-' + path, path.replace('_', ' ').capitalize())
		value = doc.get_metadata('ArchiveStyle.stats', builtin=False).content[next(i for i, v in enumerate(statsdict) if v[0] == path)].content[1] if ordered else doc.get_metadata('ArchiveStyle.stats.' + path, builtin=False)
		if isinstance(value, MetaList):
			stats.append(DefinitionItem(
				[Span(*name, identifier='ArchiveStyle.stats.' + path)],
				map(lambda item: Definition(*item), map(content.blocks, value.content))
			))
		else:
			item = content.blocks(value)
			if (item):
				stats.append(DefinitionItem(
					[Span(*name, identifier='ArchiveStyle.stats.' + path)],
					[Definition(*item)]
				))
	if len(stats):
		return DefinitionList(*stats)

def add_ambles(doc):
	amble = []
	value = metadata.blocks(doc, 'description')
	if value:
		value.insert(0, Header(*(metadata.inlines(doc, 'ArchiveStyle.localization-preamble-summary', 'Summary') + [Str(':')]), level=2))
		amble.append(Div(*value, identifier='ArchiveStyle.preamble.summary'))
	value = metadata.blocks(doc, 'ArchiveStyle.foreword')
	if value:
		value.insert(0, Header(*(metadata.inlines(doc, 'ArchiveStyle.localization-preamble-foreword', 'Foreword') + [Str(':')]), level=2))
		amble.append(Div(*value, identifier='ArchiveStyle.preamble.foreword', attributes={'role': 'note'}))
	if len(amble):
		doc.content = [
			RawBlock('<header id="ArchiveStyle.preamble">', format='html')
		] + amble + [
			RawBlock('</header>', format='html')
		] + doc.content.list
	amble = []
	value = metadata.blocks(doc, 'ArchiveStyle.afterword')
	if value:
		value.insert(0, Header(*(metadata.inlines(doc, 'ArchiveStyle.localization-preamble-afterword', 'Afterword') + [Str(':')]), level=2))
		amble.append(Div(*value, identifier='ArchiveStyle.postamble.afterword', attributes={'role': 'note'}))
	if len(amble):
		doc.content.extend([
			RawBlock('<footer id="ArchiveStyle.postamble">', format='html')
		] + amble + [
			RawBlock('</footer>', format='html')
		])

def clickthrough_wrap(doc):
	value = metadata.blocks(doc, 'ArchiveStyle.clickthrough')
	if value:
		doc.content = [
			RawBlock('<details id="ArchiveStyle.clickthrough" role="document"><summary>', format='html'),
		] + value + [
			RawBlock('</summary>', format='html'),
		] + doc.content.list + [
			RawBlock('</details>', format='html'),
			RawBlock('''<script> void function ( ) {
	var
		clickthrough = document.getElementById("ArchiveStyle.clickthrough")
		, setClickthrough = ( url, force ) => String.prototype.replace.apply(url, (force || clickthrough.open ? [/(?:[?]clickthrough=true)?(?:(?=#)|$)/, "?clickthrough=true"] : ["?clickthrough=true", ""]))
		, handleClickthrough = ( ) => {
			Array.prototype.forEach.call(document.getElementById("ArchiveStyle.nav").querySelectorAll("a[href^='.'], option"), element => {
					var attribute = element instanceof HTMLAnchorElement ? "href" : "value"
					element.setAttribute(attribute, setClickthrough(element.getAttribute(attribute))) })
			history.replaceState(null, "", setClickthrough(location.href)) }
	clickthrough.open = location.search == "?clickthrough=true"
	handleClickthrough()
	window.addEventListener("load", ( ) => {
		clickthrough.addEventListener("toggle", ( e ) => {
			handleClickthrough()
			if ( clickthrough.open ) if ( !(!e || e instanceof CustomEvent) ) if ( clickthrough.getBoundingClientRect().top > 0 ) clickthrough.scrollIntoView({ behavior: "smooth" }) })
		if ( location.hash == "#BookGen.main" ) if ( clickthrough.getBoundingClientRect().top > 0 ) clickthrough.scrollIntoView() })
	; (document.documentElement.dataset.BookGenType == "index" ? Array.prototype.slice.call(document.getElementById("ArchiveStyle.main").querySelectorAll("a")) : [ ]).concat(
	document.getElementById("ArchiveStyle.main.next")).forEach(element => { if (element) element.href = setClickthrough(element.href, true) }) }() </script>''')
		]

def add_meta(doc):
	result = [RawBlock('<header id="ArchiveStyle.meta">', format='html')]
	meta = make_metadata(doc)
	if meta:
		result.append(Div(meta, identifier='ArchiveStyle.metadata'))
	if metadata.text(doc, 'type') not in ['index', 'biblio']:
		meta = make_stats(doc)
		if meta:
			result.append(Div(*[
				RawBlock('<details><summary>', format='html'),
				Plain(*metadata.inlines(doc, 'ArchiveStyle.localization-stats', 'Chapter Stats')),
				RawBlock('</summary>', format='html'),
				meta,
				RawBlock('</details>', format='html')
			], identifier='ArchiveStyle.stats'))
	result.append(RawBlock('</header>', format='html'))
	if len(result) > 2:
		doc.content = result + doc.content.list

def add_nav(doc):
	links = [Link(
		*metadata.inlines(doc, 'ArchiveStyle.localization-nav-main', 'Main Content'),
		url=('#ArchiveStyle.clickthrough' if doc.get_metadata('ArchiveStyle.clickthrough') else '#ArchiveStyle.main'),
		classes=['screenreader'],
		attributes={'tabindex': '-1'},
		identifier='ArchiveStyle.nav.main'
	)]
	for path, name in OrderedDict([
		('index', metadata.inlines(doc, 'localization-type-index', 'Contents')),
		('first', metadata.inlines(doc, 'ArchiveStyle.localization-nav-firstarrow', u'\u21D0 ') + metadata.inlines(doc, 'ArchiveStyle.localization-nav-first', 'First Chapter')),
		('prev', metadata.inlines(doc, 'ArchiveStyle.localization-nav-prevarrow', u'\u2190 ') + metadata.inlines(doc, 'ArchiveStyle.localization-nav-prev', 'Previous Chapter')),
		('next', metadata.inlines(doc, 'ArchiveStyle.localization-nav-next', 'Next Chapter') + metadata.inlines(doc, 'ArchiveStyle.localization-nav-nextarrow', u' \u2192')),
		('last', metadata.inlines(doc, 'ArchiveStyle.localization-nav-last', 'Latest Chapter') + metadata.inlines(doc, 'ArchiveStyle.localization-nav-lastarrow', u' \u21D2')),
		('biblio', metadata.inlines(doc, 'localization-type-biblio', 'Bibliography')),
		('repository', metadata.inlines(doc, 'ArchiveStyle.localization-nav-repository', 'Source'))
	]).items():
		value = metadata.text(doc, path)
		if value:
			links.append(Link(
				*name,
				url=value + '#BookGen.main' if value[0] == '.' else value,
				identifier='ArchiveStyle.nav.' + path
			))
	value = metadata.text(doc, 'download')
	if value:
		links.append(Link(
			*metadata.inlines(doc, 'ArchiveStyle.localization-nav-download', 'Download'),
			url=doc.get_metadata('download'),
			attributes={'download': 'download'},
			identifier='ArchiveStyle.nav.download'
		))
	if doc.get_metadata('index'):
		doc.content = [
			RawBlock('<nav id="ArchiveStyle.nav">', format='html'),
			BulletList(*map(lambda link: ListItem(Plain(link)), links)),
			RawBlock('</nav>', format='html'),
			RawBlock('''<script> void function ( ) {
	"use strict"
	// This code is not necessarily sufficient to handle any EPUB navigational document, but it is sufficient to handle ours.
	var
		contents = document.getElementById('ArchiveStyle.nav.index')
		, request = new XMLHttpRequest
	if ( !contents ) return
	request.responseType = "document"
	request.addEventListener("load", ( ) => {
		var
			toc = request.responseXML.body.querySelector("nav[role=doc-toc]")
			, node = toc ? toc.firstElementChild : null
			, select = document.createElementNS("http://www.w3.org/1999/xhtml", "select")
			, item = null
			, group = null
			, content = null
		if ( !toc || !node ) return
		if ( node instanceof HTMLHeadingElement ) { node = node.nextElementSibling }
		if ( !(node instanceof HTMLOListElement) ) return
		node = node.firstElementChild
		while ( node instanceof HTMLLIElement ) {
			content = node.firstElementChild
			if ( content instanceof HTMLSpanElement ) {
				group = document.createElementNS("http://www.w3.org/1999/xhtml", "optgroup")
				group.label = content.textContent
				if ( !(!(content.nextElementSibling instanceof HTMLOListElement) || !(content.nextElementSibling.firstElementChild instanceof HTMLLIElement)) ) {
					node = content.nextElementSibling.firstElementChild
					continue }
				else group = null }
			else if ( content instanceof HTMLAnchorElement ) if ( content.origin != contents.origin || content.pathname != contents.pathname ) {
				item = document.createElementNS("http://www.w3.org/1999/xhtml", "option")
				item.textContent = content.textContent
				item.value = content.href
				; (group || select).appendChild(item) }
			if ( !(node.nextElementSibling instanceof HTMLLIElement || !group) ) {
				select.appendChild(group)
				group = null
				node = node.parentNode.parentNode.nextElementSibling }
			else node = node.nextElementSibling }
		group = document.createElementNS("http://www.w3.org/1999/xhtml", "details")
		group.id = "ArchiveStyle.index"
		item = document.createElementNS("http://www.w3.org/1999/xhtml", "summary")
		item.type = "summary"
		item.textContent = "''' + metadata.text(doc, 'ArchiveStyle.localization-nav-index', 'Chapter Index') + '''"
		group.appendChild(item)
		item = document.createElementNS("http://www.w3.org/1999/xhtml", "label")
		item.textContent = "''' + metadata.text(doc, 'ArchiveStyle.localization-nav-navigate', 'Navigate to:') + ''' "
		item.appendChild(select)
		select = item
		item = document.createElementNS("http://www.w3.org/1999/xhtml", "div")
		item.id = "ArchiveStyle.indexnav"
		item.setAttribute("hidden", "hidden")
		item.appendChild(select)
		select = document.createElementNS("http://www.w3.org/1999/xhtml", "button")
		select.type = "button"
		select.addEventListener("click", function ( ) { window.location = this.previousElementSibling.firstElementChild.value })
		select.textContent = "''' + metadata.text(doc, 'ArchiveStyle.localization-go', 'Go!') + '''"
		item.appendChild(select)
		select = document.createElementNS("http://www.w3.org/1999/xhtml", "a")
		select.setAttribute("href", contents.getAttribute("href"))
		select.textContent = contents.textContent
		item.appendChild(select)
		group.appendChild(item)
		contents.parentNode.replaceChild(group, contents)
		document.getElementById("ArchiveStyle.clickthrough").dispatchEvent(new CustomEvent("toggle")) })
	request.open("GET", contents.href)
	request.send() }() </script>''')
		] + doc.content.list

def add_header(doc):
	header = []
	for path, proc in OrderedDict([
		('series', lambda n: [RawBlock('<p id="ArchiveStyle.series">', format='html'), Plain(*n), RawBlock('</p>', format='html')]),
		('title', lambda n: [RawBlock('<p id="ArchiveStyle.title"><cite>', format='html'), Plain(Link(*n, url=metadata.text(doc, 'homepage'))) if doc.get_metadata('homepage') else Plain(*n), RawBlock('</cite></p>', format='html')]),
		('author', lambda n: [RawBlock('<p id="ArchiveStyle.author">', format='html'), Plain(Link(*n, url=metadata.text(doc, 'profile'))) if doc.get_metadata('profile') else Plain(*n), RawBlock('</p>', format='html')])
		]).items():
			value = metadata.inlines(doc, path)
			if value:
				header += proc(value)
	if len(header):
		doc.content = [
			RawBlock('<header id="ArchiveStyle.header">', format='html')
		] + header + [
			RawBlock('</header>', format='html')
		] + doc.content.list

def prepare(doc):
	updated = metadata.text(doc, 'ArchiveStyle.stats.updated')
	if updated:
		try:
			updated = datetime.fromisostring(updated)
		except:
			updated = datetime.now()
	else:
		updated = datetime.now()
	doc.stats = { # mostly tbd until finalize()
		'chars': 0,
		'paras': 0,
		'time': 0,
		'updated': updated.astimezone(timezone.utc),
		'verses': 0,
		'words': 0
	}

def action(elem, doc):
	if metadata.text(doc, 'type') != 'index':
		if isinstance(elem, Div) and 'verse' in elem.classes and not ancestor.metadata(elem):
				doc.stats['verses'] += 1
				doc.stats['paras'] += len([x for x in elem.content if isinstance(x, LineBlock)])
				elem.identifier = elem.identifier or 'ArchiveStyle.verse' + str(doc.stats['verses'])
		elif isinstance(elem, Para) and not ancestor.metadata(elem):
			doc.stats['paras'] += 1
			return Para(Span(*elem.content, identifier='ArchiveStyle.para' + str(doc.stats['paras'])))

def finalize(doc):
	set_stats(doc)
	if doc.format == 'html' or doc.format == 'html5':
		value = metadata.text(doc, 'next')
		if value:
			doc.content.append(Plain(Link(
				*(metadata.inlines(doc, 'ArchiveStyle.localization-nav-next', [Str('Next Chapter')]) + metadata.inlines(doc, 'ArchiveStyle.localization-nav-nextarrow', [Str(u' \u2192')])),
				url=value + '#BookGen.main' if value[0] == '.' else value,
				identifier='ArchiveStyle.main.next'
			)))
		doc.content = [
			RawBlock('\n<!-- BEGIN BODY -->\n<article>', format='html'),
			Div(*doc.content, identifier='ArchiveStyle.main'),
			RawBlock('</article>\n<!-- END BODY -->\n', format='html')
		]
		if metadata.text(doc, 'type') == 'index':
			add_ambles(doc)
		clickthrough_wrap(doc)
		add_meta(doc)
		add_nav(doc)
		add_header(doc)
	del doc.stats

def main(doc=None):
	return run_filter(action, doc=doc, prepare=prepare, finalize=finalize)

if __name__ == "__main__":
	main()
