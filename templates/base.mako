<!DOCTYPE html>
<html>
	<head>
		<title><%block name="title_block"/></title>
		
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<link href="${root_path}css/jhnet.css" rel="stylesheet">
		<link href="${root_path}css/bootstrap.min.css" rel="stylesheet" media="screen">
		<link href="${root_path}css/bootstrap-responsive.css" rel="stylesheet">
		
		## Include anything specified by other inheriting templates.
		<%
			for ns in context.namespaces.values():
				for incl in getattr(ns.attr, "includes", []):
					context.write(incl)
		%>
	</head>
	<body>
		${next.body()}
		
		<script src="http://code.jquery.com/jquery.js"></script>
		<script src="${root_path}js/bootstrap.js"></script>
	</body>
</html>
