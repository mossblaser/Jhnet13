<%inherit file="base.mako"/>

<%block name="title_block" filter="trim">
${title} - Jhnet
</%block>


<div class="masthead">
	<div class="container">
		<div class="clearfix">
			<a class="brand pull-left" href="${root_path}">
				<img alt="Jhnet" src="${root_path}img/jhnet_logo.png">
			</a>
			<ul class="nav nav-pills pull-right">
				% for name, url, _ in site_menu:
					% if name == site_menu_active_name:
						<li class="active"><a href="${url}">${name}</a></li>
					% else:
						<li><a href="${url}">${name}</a></li>
					% endif
				% endfor
			</ul>
		</div>
		<hr>
	</div>
</div>

<div class="content">
	<div class="container">
		${next.body()}
	</div>
</div>

<div class="footer">
	<div class="container">
		<hr>
		<p class="text-center muted">
			<small>
				&copy; 2013 Jonathan Heathcote
				## Include additional copyrights
				<%
					for ns in context.namespaces.values():
						for incl in getattr(ns.attr, "copyright", []):
							context.write("<br>" + incl)
				%>
			</small>
		</p>
	</div>
</div>
