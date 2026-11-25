import sys,re,json
stem=sys.argv[1]; start_pat=sys.argv[2] if len(sys.argv)>2 else None; end_pat=sys.argv[3] if len(sys.argv)>3 else None
sys.argv=["x","none"]
exec(open("sweep.py",encoding="utf-8").read().split('if sys.argv[1] == "fetch"')[0])
for s,fm,rows,urls in posts():
    if s!=stem: continue
    best=max(urls,key=lambda u:len(page_text(u) or ""))
    raw=decode(open(cache_path(best),"rb").read())
    raw=re.sub(r"(?is)<(script|style|noscript|nav|header|footer)\b.*?</\1>"," ",raw)
    raw=re.sub(r"(?i)</(p|div|li|h\d|blockquote)>|<br\s*/?>","\n",raw)
    t=html.unescape(re.sub(r"<[^>]+>"," ",raw))
    ps=[re.sub(r"[ \t\u00a0]+"," ",p).strip() for p in t.split("\n")]
    ps=[p for p in ps if p]
    if start_pat:
        a=next(i for i,p in enumerate(ps) if re.search(start_pat,p)); ps=ps[a:]
    if end_pat:
        b=next((i for i,p in enumerate(ps) if re.search(end_pat,p)),len(ps)); ps=ps[:b]
    rn={norm(r.get("original")):i for i,r in enumerate(rows)}
    print(best,len(ps))
    for k,p in enumerate(ps):
        print(k,"[row %s]"%rn.get(norm(p)) if norm(p) in rn else "","|",p)
