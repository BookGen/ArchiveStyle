#!/usr/bin/env python3

"""
Pandoc HTML filters.
"""

from panflute import *
from collections import OrderedDict

def contentFromMeta(meta):
	if isinstance(meta, MetaBlocks):
		return meta.content.list
	if isinstance(meta, MetaBool):
		return Plain(Str(u'\u2B55' if meta.boolean else u'\u274C'))
	if isinstance(meta, MetaInlines):
		return Plain(*meta.content)
	if isinstance(meta, MetaList):
		content = reduce(lambda items, item: items.append(item), meta.content.list, [])
		return content
	if isinstance(meta, MetaMap):
		content = []
		for key, value in meta.content.dict:
			if isinstance(value, MetaList):
				content.append(DefinitionItem([Str(key)], reduce(lambda item_contents, item_content: item_contents + [Definition(*item_content) if isinstance(item_content, list) else Definition(item_content)], map(contentFromMeta, value.content.list), [])))
			else:
				item_content = contentFromMeta(value)
				content.append(DefinitionItem([Str(key)], [Definition(*item_content) if isinstance(item_content, list) else Definition(item_content)]))
		return DefinitionList(*content)
	if isinstance(meta, MetaString):
		return Plain(Str(meta.text))

def action(elem, doc):
	None

def finalize(doc):
	if doc.format == 'html' or doc.format == 'html5':
		metadata = []
		ordered_metadata = OrderedDict([
			('rating', doc.get_metadata('ArchiveStyle.localization.rating', 'Rating')),
			('warning', doc.get_metadata('ArchiveStyle.localization.warning', 'Warnings')),
			('category', doc.get_metadata('ArchiveStyle.localization.category', 'Categories')),
			('fandom', doc.get_metadata('ArchiveStyle.localization.fandom', 'Fandoms')),
			('relationship', doc.get_metadata('ArchiveStyle.localization.relationship', 'Relationship')),
			('character', doc.get_metadata('ArchiveStyle.localization.character', 'Characters')),
			('tagged', doc.get_metadata('ArchiveStyle.localization.tagged', 'Additional Tags'))
		])
		metadict = doc.get_metadata('ArchiveStyle.metadata')
		keys = []
		ordered = False
		if isinstance(metadict, dict):
			keys = ordered_metadata.keys() + list(set(doc.get_metadata('ArchiveStyle.metadata', dict()).keys()) - set(ordered_metadata.keys()))
		elif isinstance(metadict, list):
			keys = OrderedDict(map(lambda a: tuple(a), metadict)).keys()
			ordered = True
		for path in keys:
			name = ordered_metadata.get(path, doc.get_metadata('ArchiveStyle.localization.' + path, path.replace('_', ' ').title()))
			value = doc.get_metadata('ArchiveStyle.metadata', builtin=False).content.list[next(i for i, v in enumerate(metadict) if v[0] == path)].content.list[1] if ordered else doc.get_metadata('ArchiveStyle.metadata.' + path, builtin=False)
			if isinstance(value, MetaList):
				metadata.append(DefinitionItem([Span(Str(name), identifier='ArchiveStyle.metadata.' + path)], reduce(lambda item_contents, item_content: item_contents + [Definition(*item_content) if isinstance(item_content, list) else Definition(item_content)], map(contentFromMeta, value.content.list), [])))
			else:
				item_content = contentFromMeta(value)
				if (item_content):
					metadata.append(DefinitionItem([Span(Str(name), identifier='ArchiveStyle.metadata.' + path)], [Definition(*item_content) if isinstance(item_content, list) else Definition(item_content)]))
		content = doc.content.list
		value = doc.get_metadata('next')
		if value:
			content = content + [
				Plain(Link(Str(doc.get_metadata('ArchiveStyle.localization.next', doc.get_metadata('localization.next', u'Next Chapter')) + doc.get_metadata('ArchiveStyle.localization.nextarrow', u' \u2192')), url=value + '#BookGen.main' if value[0] == '.' else value, identifier='ArchiveStyle.main.next'))
			]
		content = [
			RawBlock('\n<!-- BEGIN BODY -->\n<article>', format='html'),
			Div(*content, identifier='ArchiveStyle.main'),
			RawBlock('</article>\n<!-- END BODY -->\n', format='html')
		]
		header = []
		footer = []
		if doc.get_metadata('type') == 'index':
			value = contentFromMeta(doc.get_metadata('ArchiveStyle.summary', builtin=False))
			if not value:
				value = doc.get_metadata('description')
				if value:
					value = Plain(Str(value))
			if value:
				value = [
					Header(Str(doc.get_metadata('ArchiveStyle.localization.summary', 'Summary')), level=2)
				] + (value if isinstance(value, list) else [value])
				header.append(Div(*value, identifier='ArchiveStyle.summary'))
			value = contentFromMeta(doc.get_metadata('ArchiveStyle.foreword', builtin=False))
			if value:
				value = [
					Header(Str(doc.get_metadata('ArchiveStyle.localization.foreword', 'Foreword')), level=2)
				] + (value if isinstance(value, list) else [value])
				header.append(Div(*value, identifier='ArchiveStyle.foreword', attributes={'role': 'note'}))
			value = contentFromMeta(doc.get_metadata('ArchiveStyle.afterword', builtin=False))
			if value:
				value = [
					Header(Str(doc.get_metadata('ArchiveStyle.localization.afterword', 'Afterword')), level=2)
				] + (value if isinstance(value, list) else [value])
				footer.append(Div(*value, identifier='ArchiveStyle.afterword', attributes={'role': 'note'}))
		if len(header):
			content = [
				RawBlock('<header id="ArchiveStyle.preamble">', format='html')
			] + header + [
				RawBlock('</header>', format='html')
			] + content
		if len(footer):
			content += [
				RawBlock('<footer id="ArchiveStyle.postamble">', format='html')
			] + footer + [
				RawBlock('</footer>', format='html')
			]
		value = contentFromMeta(doc.get_metadata('ArchiveStyle.clickthrough', builtin=False))
		if value:
			content = [
				RawBlock('<details id="ArchiveStyle.clickthrough" role="document"><summary>', format='html'),
				Div(*value) if isinstance(value, list) else Div(value),
				RawBlock('</summary>', format='html'),
			] + content + [
				RawBlock('</details>', format='html'),
				RawBlock('''<script> void function ( ) {
	var
		clickthrough = document.getElementById("ArchiveStyle.clickthrough")
		, setClickthrough = ( url, force ) => String.prototype.replace.apply(url, (force || clickthrough.open ? [/(?:[?]clickthrough=true)?(?:(?=#)|$)/, "?clickthrough=true"] : ["?clickthrough=true", ""]))
		, handleClickthrough = ( ) => {
			Array.prototype.forEach.call(document.getElementById("ArchiveStyle.pagenav").querySelectorAll("a[href^='.'], option"), element => {
					var attribute = element instanceof HTMLAnchorElement ? "href" : "value"
					element.setAttribute(attribute, setClickthrough(element.getAttribute(attribute))) })
			history.replaceState(null, "", setClickthrough(location.href)) }
	clickthrough.open = location.search == "?clickthrough=true"
	clickthrough.addEventListener("toggle", ( e ) => {
		handleClickthrough()
		if ( clickthrough.open ) if ( !(!e || e instanceof CustomEvent) ) clickthrough.scrollIntoView({ behavior: "smooth" }) })
	handleClickthrough()
	window.addEventListener("load", ( ) => { if ( location.hash == "#BookGen.main" ) clickthrough.scrollIntoView() })
	; (document.documentElement.dataset.BookGenType == "index" ? Array.prototype.slice.call(document.getElementById("ArchiveStyle.main").querySelectorAll("a")) : [ ]).concat(
	document.getElementById("ArchiveStyle.main.next")).forEach(element => element.href = setClickthrough(element.href, true)) }() </script>''')
			]
		if len(metadata):
			content = [
				RawBlock('<header id="ArchiveStyle.metadata">', format='html'),
				DefinitionList(*metadata),
				RawBlock('</header>', format='html')
			] + content
		links = [Link(Str(doc.get_metadata('ArchiveStyle.localization.main', doc.get_metadata('localization.main', 'Main Content'))), url=('#ArchiveStyle.clickthrough' if doc.get_metadata('ArchiveStyle.clickthrough') else '#ArchiveStyle.main'), classes=['screenreader'], attributes={'tabindex': '-1'})]
		for path, name in OrderedDict([
			('index', doc.get_metadata('localization.index', 'Contents')),
			('first', doc.get_metadata('ArchiveStyle.localization.firstarrow', u'\u21D0 ') + doc.get_metadata('ArchiveStyle.localization.first', doc.get_metadata('localization.first', 'First Chapter'))),
			('prev', doc.get_metadata('ArchiveStyle.localization.prevarrow', u'\u2190 ') + doc.get_metadata('ArchiveStyle.localization.prev', doc.get_metadata('localization.prev', 'Previous Chapter'))),
			('next', doc.get_metadata('ArchiveStyle.localization.next', doc.get_metadata('localization.next', u'Next Chapter')) + doc.get_metadata('ArchiveStyle.localization.nextarrow', u' \u2192')),
			('last', doc.get_metadata('ArchiveStyle.localization.last', doc.get_metadata('localization.last', u'Latest Chapter')) + doc.get_metadata('ArchiveStyle.localization.lastarrow', u' \u21D2')),
			('biblio', doc.get_metadata('ArchiveStyle.localization.biblio', doc.get_metadata('localization.biblio', 'Bibliography'))),
			('repository', doc.get_metadata('ArchiveStyle.localization.repository', doc.get_metadata('localization.repository', 'Source')))
 		]).items():
			value = doc.get_metadata(path)
			if value:
				links.append(Link(Str(name), url=value + '#BookGen.main' if value[0] == '.' else value, identifier='ArchiveStyle.pagenav.' + path))
		if doc.get_metadata('download'):
			links.append(Link(Str(doc.get_metadata('ArchiveStyle.localization.download', doc.get_metadata('localization.download', 'Download'))), url=doc.get_metadata('download'), attributes={'download': 'download'}))
		content = [
			RawBlock('<nav id="ArchiveStyle.pagenav">', format='html'),
			BulletList(*map(lambda l: ListItem(Plain(l)), links)),
			RawBlock('</nav>', format='html')
		] + ([
			RawBlock('''<script> void function ( ) {
	"use strict"
	// This code is not necessarily sufficient to handle any EPUB navigational document, but it is sufficient to handle ours.
	var
		contents = document.getElementById('ArchiveStyle.pagenav.index')
		, request = new XMLHttpRequest
	if ( !contents ) return
	request.responseType = "document"
	request.addEventListener("load", ( ) => {
		var
			toc = request.responseXML.body.querySelector("nav[role=doc-toc]")
			, node = toc ? toc.firstElementChild : null
			, select = document.createElementNS("http://www.w3.org/1999/xhtml", "select")
			, title = "''' + doc.get_metadata('ArchiveStyle.localization.contents', doc.get_metadata('localization.index', 'Contents')) + '''"
			, item = null
			, group = null
			, content = null
		if ( !toc || !node ) return
		if ( node instanceof HTMLHeadingElement ) {
			title = node.textContent
			node = node.nextElementSibling }
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
		item.textContent = "''' + doc.get_metadata('ArchiveStyle.localization.index', 'Chapter Index') + '''"
		group.appendChild(item)
		item = document.createElementNS("http://www.w3.org/1999/xhtml", "label")
		item.textContent = "''' + doc.get_metadata('ArchiveStyle.localization.navigate', 'Navigate to:') + ''' "
		item.appendChild(select)
		select = item
		item = document.createElementNS("http://www.w3.org/1999/xhtml", "div")
		item.id = "ArchiveStyle.indexnav"
		item.setAttribute("hidden", "hidden")
		item.appendChild(select)
		select = document.createElementNS("http://www.w3.org/1999/xhtml", "button")
		select.type = "button"
		select.addEventListener("click", function ( ) { window.location = this.previousElementSibling.firstElementChild.value })
		select.textContent = "''' + doc.get_metadata('ArchiveStyle.localization.contents', 'Go!') + '''"
		item.appendChild(select)
		select = document.createElementNS("http://www.w3.org/1999/xhtml", "a")
		select.setAttribute("href", contents.getAttribute("href"))
		select.textContent = title
		item.appendChild(select)
		group.appendChild(item)
		contents.parentNode.replaceChild(group, contents)
		document.getElementById("ArchiveStyle.clickthrough").dispatchEvent(new CustomEvent("toggle")) })
	request.open("GET", contents.href)
	request.send() }() </script>''')
		] + content if doc.get_metadata('index') else content)
		header = []
		for path, proc in OrderedDict([
			('series', lambda n: [RawBlock('<p id="ArchiveStyle.series">', format='html'), Plain(n), RawBlock('</p>', format='html')]),
			('title', lambda n: [RawBlock('<p id="ArchiveStyle.title"><cite>', format='html'), Plain(Link(n, url=doc.get_metadata('homepage')) if doc.get_metadata('homepage') else n), RawBlock('</cite></p>', format='html')]),
			('author', lambda n: [RawBlock('<p id="ArchiveStyle.author">', format='html'), Plain(Link(n, url=doc.get_metadata('profile')) if doc.get_metadata('profile') else n), RawBlock('</p>', format='html')])
 		]).items():
 			value = doc.get_metadata(path)
 			if value:
 				header += proc(Str(value))
		if len(header):
			content = [
				RawBlock('<header id="ArchiveStyle.header">', format='html')
			] + header + [
				RawBlock('</header>', format='html')
			] + content
		doc.content = content

def main(doc=None):
	return run_filter(action, doc=doc, finalize=finalize)

if __name__ == "__main__":
	main()
