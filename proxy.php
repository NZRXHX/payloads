<?php
$file_url = 'http://10.0.3.4/prog.exe';
$file_name = 'prog.exe';
$file_content = file_get_contents($file_url);
if ($file_content === false) {
    die('Error: Could not fetch the file from the source server.');
}
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="' . $file_name . '"');
header('Content-Length: ' . strlen($file_content));
header('Content-Transfer-Encoding: binary');
header('Expires: 0');
header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
header('Pragma: public');
header('X-Content-Type-Options: nosniff');
echo $file_content;
exit;
?>
