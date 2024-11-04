<?php
require_once "backend.php"

function ledServiceStatus() {
	$rc = 0;
	exec("sudo systemctl status led.service", null, $rc);
	if($rc == 0) return "running";
	elseif($rc == 3) return "stopped";
	else return "error";
}
function startLedService() {
	exec("sudo systemctl start led.service", null, $rc);
}
function stopLedServicse() {
	exec("sudo systemctl stop led.service", null, $rc);
}

?>
