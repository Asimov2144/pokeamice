param(
  [switch]$Full
)

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = Join-Path $root ".venv-mineru\Scripts\python.exe"
$cacheRoot = Join-Path $root ".mineru-cache"

New-Item -ItemType Directory -Force `
  -Path `
    (Join-Path $cacheRoot "modelscope"), `
    (Join-Path $cacheRoot "modelscope-credentials") | Out-Null

$env:MODELSCOPE_CACHE = Join-Path $cacheRoot "modelscope"
$env:MODELSCOPE_CREDENTIALS_PATH = Join-Path $cacheRoot "modelscope-credentials"
$env:MINERU_TOOLS_CONFIG_JSON = Join-Path $cacheRoot "mineru.json"
$env:MINERU_MODEL_SOURCE = "modelscope"

$mode = if ($Full) { "full" } else { "minimal" }
Write-Host "Downloading MinerU pipeline models: $mode"
Write-Host "Cache: $env:MODELSCOPE_CACHE"

& $python -c @"
from modelscope import snapshot_download

repo = "OpenDataLab/PDF-Extract-Kit-1.0"
patterns = [
    "models/Layout/PP-DocLayoutV2",
    "models/Layout/PP-DocLayoutV2/*",
    "models/OCR/paddleocr_torch",
    "models/OCR/paddleocr_torch/*",
]

if "$mode" == "full":
    patterns += [
        "models/MFR/unimernet_hf_small_2503",
        "models/MFR/unimernet_hf_small_2503/*",
        "models/MFR/pp_formulanet_plus_m",
        "models/MFR/pp_formulanet_plus_m/*",
        "models/TabRec/SlanetPlus",
        "models/TabRec/SlanetPlus/*",
        "models/TabRec/UnetStructure",
        "models/TabRec/UnetStructure/*",
        "models/TabCls/paddle_table_cls",
        "models/TabCls/paddle_table_cls/*",
    ]

path = snapshot_download(repo, allow_patterns=patterns)
print(path)
"@
