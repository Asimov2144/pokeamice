$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$env:BUNDLE_PATH = "vendor/bundle"
$env:BUNDLE_BIN = "vendor/bundle/bin"
$env:BUNDLE_SYSTEM_BINDIR = Join-Path $root "vendor\bundle\bin"
$env:TMPDIR = Join-Path $root ".ruby-tmp"
$env:TMP = $env:TMPDIR
$env:TEMP = $env:TMPDIR
$env:PATH = "C:\Ruby33-x64\msys64\usr\bin;C:\Ruby33-x64\msys64\ucrt64\bin;$env:BUNDLE_SYSTEM_BINDIR;$env:PATH"

Set-Location $root
bundle exec ruby "vendor\bundle\ruby\3.3.0\gems\jekyll-4.4.1\exe\jekyll" serve --host 127.0.0.1 --port 4000 --skip-initial-build
