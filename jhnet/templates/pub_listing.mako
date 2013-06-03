<%inherit file="normal.mako"/>

<h1>${heading}</h1>
<!-- This is not a blog... -->

${readme}

<div class="row">
	<div class="toc span2">
		<ul class="nav nav-list">
			<li class="nav-header">Select by Tag</li>
			% for name, url, active in tags:
				<li class="${"active" if active else ""}"><a href="${url}">${name}</a></li>
			% endfor
		</ul>
	</div>
	
	<div class="listing span10">
		% for title, subtitle, url, img, img_alt, abstract, pub_tags in publications:
			<div class="media">
				% if img is not None:
					<a class="pull-left" href="${url}">
						<span class="media-object">
							<img src="${img}" alt="${img_alt}">
						</span>
					</a>
				% endif
				<div class="media-body">
					<h2 class="media-heading"><a href="${url}">
						${title}
						% if subtitle is not None:
							<small>${subtitle}</small>
						% endif
					</a></h2>
					
					${abstract}
					
					<ul class="inline">
						% for tag, tag_url in pub_tags:
						<a href="${tag_url}" class="label">${tag}</a>
						% endfor
					</ul>
				</div>
			</div>
		% endfor
	</div>
</div>
