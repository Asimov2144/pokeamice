import sys,re,json
sys.argv=["x","none"]
exec(open("sweep.py",encoding="utf-8").read().split('if sys.argv[1] == "fetch"')[0])
sc=json.load(open(os.path.join(OUT,"scores.json"),encoding="utf-8"))
def paras(txt):
    ps=[re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n|\s{3,}",txt)]
    return [p for p in ps if len(norm(p))>=25]
res=[]
for s,fm,rows,urls in posts():
    v=sc.get(s)
    if not v or v["status"]!="ok" or not v["flagged"] or "-scan-" in s: continue
    txt="".join(page_text(u) or "" for u in urls)
    P=paras(txt); PN=[norm(p) for p in P]
    near=[];
    for i,cov,t,_ in v["flagged"]:
        o=str(rows[i].get("original")); k=k_for(o); g=grams(norm(o),k)
        if not g: continue
        best=0;bj=None
        for j,pn in enumerate(PN):
            c=len(g&grams(pn,k))/len(g)
            if c>best: best,bj=c,j
        if best>=0.2: near.append((i,round(best,2)))
    res.append((len(near),len(v["flagged"]),v["checked"],s,near[:12]))
res.sort(reverse=True)
for r in res:
    if r[0]: print(r[0],"/",r[1],"flagged of",r[2],r[3],r[4])
json.dump(res,open(os.path.join(OUT,"near.json"),"w",encoding="utf-8"),ensure_ascii=False)
