<%inherit file="normal.mako"/>

<h1>${title}</h1>

${readme}

<p>
	% for link, crumb in breadcrumb:
		<a href="${link}" class="btn btn-small">${crumb}</a>
	% endfor
</p>

<div class="misc">
	<table class="table table-condensed table-hover" data-provides="rowlink">
		
		<thead>
			<tr>
				<th>
					<a href="?sort=name&${toggle_reverse}">Name <span class="${name_class}"></span></a>
				</th>
				<th class="span3">
					<a href="?sort=date&${toggle_reverse}">Date Uploaded <span class="${date_class}"></span></a>
				</th>
				<th class="span2">
					<a href="?sort=size&${toggle_reverse}">Size <span class="${size_class}"></span></a>
				</th>
			</tr>
		</thead>
		
		<tbody>
			% for file_name, modtime, size in file_list:
				<tr>
					<td><a class="rowlink" href="${file_name}">${file_name | h}</a></td>
					<td>${modtime | h}</td>
					<td>${size | h}</td>
				</tr>
			% endfor
		</tbody>
		
	</table>
</div>
