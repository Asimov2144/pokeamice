import urllib.request

url = "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_HvW9bZyNETcddubLwKAMTR17n_BTnW_HqddHyYDzibaBQpWJuv267QYnRtW7VUlwt_EQkoYmgU1M6FHYY30ygYuYBMmgl2xK7aw2NhCngp9ryVzUu0yATlrdxdKIYw=="
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print("Final URL:", resp.geturl())
except Exception as e:
    print("Err:", e)
