<!DOCTYPE html>

<?php require_once "backend.php" ?>


<html><head>
	<title> LED Control dashboard </title>

	<script src="https://unpkg.com/htmx.org@2.0.3"></script>
</head><body>
	<h1>The ultimate LED control dashboard™</h1>

	<h2> LED Strip is </h2>

	<button hx-post="/api.php?action=setAllLEDs,all=on" hx-swap="outerHTML">
		LEDs on
	</button>

</body></html>
