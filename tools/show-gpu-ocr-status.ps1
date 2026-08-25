$nvidiaSmi = Get-ChildItem -LiteralPath "C:\WINDOWS\System32\DriverStore\FileRepository" -Recurse -Filter nvidia-smi.exe -ErrorAction SilentlyContinue |
  Select-Object -First 1 -ExpandProperty FullName

if ($nvidiaSmi) {
  Write-Host "GPU status:"
  & $nvidiaSmi
} else {
  Write-Host "nvidia-smi.exe not found in DriverStore."
}

Write-Host ""
Write-Host "Python / OCR-like processes:"
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" -ErrorAction SilentlyContinue |
  Select-Object ProcessId, Name, CommandLine |
  Format-List
