import sys,re,json
sys.argv=["x","none"]
exec(open("sweep.py",encoding="utf-8").read().split('if sys.argv[1] == "fetch"')[0])
STEM="2014-08-22-interview-niconico-gamefreak-origins-masuda"
for s,fm,rows,urls in posts():
    if s!=STEM: continue
    raw=decode(open(cache_path(urls[0]),"rb").read())
    raw=re.sub(r"(?is)<(script|style|noscript|nav|header|footer)\b.*?</\1>"," ",raw)
    raw=re.sub(r"(?i)</(p|div|li|h\d|blockquote)>|<br\s*/?>","\n",raw)
    t=html.unescape(re.sub(r"<[^>]+>"," ",raw))
    ps=[re.sub(r"[ \t\u00a0\u3000]+"," ",p).strip() for p in t.split("\n")]
    ps=[p for p in ps if p]
    a=next(i for i,p in enumerate(ps) if p.startswith("80 年代末"))
    b=next(i for i,p in enumerate(ps) if i>a and re.search(r"ポケモンメモ|コメントを|記事一覧|Copyright|この記事をシェア|^関連",p) )
    ps=ps[a:b]
    out=[]
    for k,p in enumerate(ps):
        g=grams(norm(p),6)
        best=-1;bs=0
        for i,r in enumerate(rows):
            go=grams(norm(r.get("original")),6)
            if not g or not go: continue
            sc=len(g&go)/len(g)
            if sc>bs: bs,best=sc,i
        out.append({"k":k,"p":p,"row":best if bs>=0.5 else None,"sc":round(bs,2)})
    json.dump(out,open("niconico_paras.json","w",encoding="utf-8"),ensure_ascii=False)
    print(len(ps),"b",b)
    for o in out: print(o["k"],o["row"],o["sc"],"|",o["p"][:60] if o["sc"]>=0.9 else "")
