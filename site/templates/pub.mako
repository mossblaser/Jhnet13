<%inherit file="normal.mako"/>

<div class="row">
	## Table of contents
	% if toc is not None:
		<div class="toc span3 pull-right">
			<ul class="nav nav-list">
				<li class="nav-header">Table of Contents</li>
				<ul class="nav nav-list">
				% for toc_level, toc_entry, toc_anchor in toc:
					<li style="padding-left:${toc_level-1}em"><a href="#${toc_anchor}">${toc_entry}</a></li>
				% endfor
				</ul>
			</ul>
		</div>
	% endif
	
	<div class="article span9">
		${content}
	</div>
</div>

