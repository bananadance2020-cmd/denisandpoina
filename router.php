<?php
$path = parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH);
$ext = pathinfo($path, PATHINFO_EXTENSION);
if (file_exists($_SERVER["DOCUMENT_ROOT"] . $path) && $path !== '/') {
    return false; // serve the requested resource as-is.
} else if ($path === '/' || $path === '/index.html') {
    include 'index.html';
} else {
    include 'proxy.php';
}
