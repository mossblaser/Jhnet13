<%inherit file="base.mako"/>

<%block name="title_block" filter="trim">
Jhnet
</%block>

<%block name="includes">
	<style>
		div.homepage div.masthead {
			text-align : center;
			
			margin-top : 100px;
			
			padding-top    : 30px;
			padding-bottom : 30px;
			
			border-top-style : solid;
		}
		
		div.homepage .lead {
			padding-top    : 10px;
			padding-bottom : 10px;
		}
		
		ul.home-buttons {
			list-style : none;
			margin-bottom : -20px;
		}
		
		ul.home-buttons li{
			display : inline;
			padding-right  : 20px;
			padding-left   : 20px;
		}
		
		ul.home-buttons li a{
			display        : inline-block;
			min-width      : 42px;
			padding-top    : 50px;
			padding-bottom : 20px;
			
			background-repeat : no-repeat;
			background-position : top center;
		}
		
		.home-buttons-about    { background : url("img/icon_about.png"); }
		.home-buttons-projects { background : url("img/icon_projects.png"); }
		.home-buttons-articles { background : url("img/icon_articles.png"); }
		.home-buttons-misc     { background : url("img/icon_misc.png"); }
		
		</style>
</%block>

<div class="content homepage">
	<div class="masthead">
		<h1><img src="img/jhnet_logo_big.png" alt="Jhnet"></h1>
		
		<p class="lead">Assorted Projects and Stuff by <strong>Jonathan
		Heathcote</strong></p>
		
		<ul class="home-buttons">
			% for name, url, css_class in site_menu:
				<li><a href="${url}" class="${css_class}">${name}</a></li>
			% endfor
		</ul>
		
	</div>
</div>
