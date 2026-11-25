import sys,re,json
stem=sys.argv[1]; sys.argv=["x","none"]
exec(open("sweep.py",encoding="utf-8").read().split('if sys.argv[1] == "fetch"')[0])
sc=json.load(open(os.path.join(OUT,"scores.json"),encoding="utf-8"))
def paras(txt):
    ps=[re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n|\s{3,}",txt)]
    return [p for p in ps if len(norm(p))>=25]
for s,fm,rows,urls in posts():
    if s!=stem: continue
    txt="".join(page_text(u) or "" for u in urls)
    P=paras(txt)
    PN=[norm(p) for p in P]
    full=norm(txt)
    flagged={f[0] for f in sc[s]["flagged"]}
    print(urls)
    for i in sorted(flagged):
        o=str(rows[i].get("original"))
        k=k_for(o); g=grams(norm(o),k)
        best=max(range(len(P)),key=lambda j:len(g&grams(PN[j],k)),default=None)
        sc_=len(g&grams(PN[best],k))/len(g) if best is not None else 0
        print("--",i,rows[i].get("type",""),rows[i].get("speaker",""),"cov%.2f"%sc_)
        print("  POST:",o[:int(sys.argv[2]) if False else 260])
        if sc_>0.15: print("  PAGE:",P[best][:260])
