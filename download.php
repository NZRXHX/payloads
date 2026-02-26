
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

<?php

$file_url = 'http://10.0.3.4/prog.exe';
$file_name = 'prog.exe';
$log_entry = date('Y-m-d H:i:s') . ' - IP: ' . $_SERVER['REMOTE_ADDR'] . ' - Downloaded: ' . $file_name . "\n";
@file_put_contents('download_log.txt', $log_entry, FILE_APPEND);
$remote_file = @fopen($file_url, 'rb');

if (!$remote_file) {
    ?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>Download Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .error { color: red; }
            a { color: blue; }
        </style>
    </head>
    <body>
        <h2 class="error">Download Error</h2>
        <p>Sorry, the file could not be retrieved from the source server.</p>
        <p>Please <a href="index.html">click here</a> to try again.</p>
    </body>
    </html>
    <?php
    exit;
}

// Get the file size from the remote server (if available)
$headers = stream_get_meta_data($remote_file);
$file_size = 0;
foreach ($headers['wrapper_data'] as $header) {
    if (stripos($header, 'Content-Length:') === 0) {
        $file_size = (int)substr($header, 15);
        break;
    }
}

header('Content-Description: File Transfer');
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename="' . $file_name . '"');
if ($file_size > 0) {
    header('Content-Length: ' . $file_size);
}
header('Content-Transfer-Encoding: binary');
header('Expires: 0');
header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
header('Pragma: public');
header('X-Content-Type-Options: nosniff');

// Clear output buffer
if (ob_get_level()) {
    ob_end_clean();
}

while (!feof($remote_file)) {
    $buffer = fread($remote_file, 8192); // 8KB chunks
    echo $buffer;
    flush();
}

fclose($remote_file);
exit;
?>
