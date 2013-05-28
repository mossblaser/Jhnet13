<%inherit file="normal.mako"/>

<div class="row">
	<div class="article span9">
		${content}
	</div>
	## Table of contents
	% if toc is not None:
		<div class="toc span3">
			<ul class="nav nav-list">
				<li class="nav-header">Table of Contents</li>
				% for toc_entry, toc_anchor in toc:
					<li><a href="#${toc_anchor}">${toc_entry}</a></li>
				% endfor
			</ul>
		</div>
	% endif
</div>

