<?php
// Recipe import helper for the Pantry Planner.
// The page calls import.php?url=... to read a recipe page that the browser
// can't fetch directly. It only fetches public http(s) pages, refuses private
// and local addresses (including after redirects), and caps size and time.
// Requires PHP with the curl extension. Delete this file to turn the feature off.

header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

function fail($code, $msg) { http_response_code($code); header('Content-Type: text/plain'); echo $msg; exit; }

function public_url($url) {
  $p = parse_url($url);
  if (!$p || !isset($p['scheme'], $p['host'])) return false;
  if (!in_array(strtolower($p['scheme']), ['http', 'https'], true)) return false;
  if (isset($p['user']) || isset($p['pass'])) return false;
  $port = $p['port'] ?? null;
  if ($port !== null && !in_array((int)$port, [80, 443], true)) return false;
  $ips = gethostbynamel($p['host']);
  if (!$ips) return false;
  foreach ($ips as $ip) {
    if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) return false;
  }
  return $ips[0];
}

// Only answer requests coming from this site's own pages.
$ref = $_SERVER['HTTP_REFERER'] ?? '';
$self = $_SERVER['HTTP_HOST'] ?? '';
if ($ref === '' || parse_url($ref, PHP_URL_HOST) !== $self) fail(403, 'Forbidden');

$url = trim($_GET['url'] ?? '');
if ($url === '' || strlen($url) > 2000) fail(400, 'Missing url');
if (!function_exists('curl_init')) fail(501, 'curl not available');

$max = 3 * 1024 * 1024;
for ($hop = 0; $hop < 4; $hop++) {
  $p = parse_url($url);
  $ip = public_url($url);
  if (!$ip) fail(400, 'That address is not allowed');
  $port = $p['port'] ?? (strtolower($p['scheme']) === 'https' ? 443 : 80);
  $body = '';
  $ch = curl_init($url);
  curl_setopt_array($ch, [
    CURLOPT_RESOLVE => [$p['host'] . ':' . $port . ':' . $ip], // pin the checked IP
    CURLOPT_RETURNTRANSFER => false,
    CURLOPT_FOLLOWLOCATION => false,
    CURLOPT_HEADER => false,
    CURLOPT_CONNECTTIMEOUT => 5,
    CURLOPT_TIMEOUT => 12,
    CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
    CURLOPT_USERAGENT => 'Mozilla/5.0 (compatible; PantryPlannerImport/1.0)',
    CURLOPT_HTTPHEADER => ['Accept: text/html,application/xhtml+xml'],
    CURLOPT_ENCODING => '',
    CURLOPT_WRITEFUNCTION => function ($ch, $chunk) use (&$body, $max) {
      $body .= $chunk;
      return strlen($body) > $max ? 0 : strlen($chunk);
    },
  ]);
  curl_exec($ch);
  $status = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
  $next = curl_getinfo($ch, CURLINFO_REDIRECT_URL);
  $type = curl_getinfo($ch, CURLINFO_CONTENT_TYPE) ?: '';
  curl_close($ch);
  if ($status >= 300 && $status < 400 && $next) { $url = $next; continue; }
  if ($status !== 200) fail(502, 'The recipe site answered ' . $status);
  if (stripos($type, 'html') === false) fail(415, 'Not a web page');
  header('Content-Type: text/html; charset=utf-8');
  echo $body;
  exit;
}
fail(508, 'Too many redirects');
