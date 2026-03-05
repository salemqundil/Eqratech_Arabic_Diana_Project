# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, csv, json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

FATHA="َ"; DAMMA="ُ"; KASRA="ِ"; SUKUN="ْ"; SHADDA="ّ"

PERSONS14 = [
    ("3ms","sg","m"),("3fs","sg","f"),("3dm","du","m"),("3df","du","f"),
    ("3mp","pl","m"),("3fp","pl","f"),("2ms","sg","m"),("2fs","sg","f"),
    ("2dm","du","m"),("2df","du","f"),("2mp","pl","m"),("2fp","pl","f"),
    ("1s","sg","-"),("1p","pl","-"),
]

@dataclass(frozen=True)
class VerbSpec:
    lemma: str
    root: Tuple[str,str,str]
    vtype: str              # sound|hollow|def_yaa|def_waaw|assimilated|hamzated|doubled
    past_pattern: str       # fa3ala|fa3ila|fa3ula|irreg
    pres_class: str         # a|i|u
    notes: Optional[str]=None

LEXICON: Dict[str,VerbSpec] = {
    "كَتَبَ": ("كَتَبَ",("ك","ت","ب"),"sound","fa3ala","u","كتب يَكْتُبُ"),
    "جَلَسَ": ("جَلَسَ",("ج","ل","س"),"sound","fa3ala","i","جلس يَجْلِسُ"),
    "دَخَلَ": ("دَخَلَ",("د","خ","ل"),"sound","fa3ala","u","دخل يَدْخُلُ"),
    "عَلِمَ": ("عَلِمَ",("ع","ل","م"),"sound","fa3ila","a","عَلِمَ يَعْلَمُ"),
    "حَسُنَ": ("حَسُنَ",("ح","س","ن"),"sound","fa3ula","u","حَسُنَ يَحْسُنُ"),
    "قَرَأَ": ("قَرَأَ",("ق","ر","أ"),"hamzated","fa3ala","a","قَرَأَ يَقْرَأُ"),
    "قَالَ": ("قَالَ",("ق","و","ل"),"hollow","irreg","u","قال يَقُولُ"),
    "بَاعَ": ("بَاعَ",("ب","ي","ع"),"hollow","irreg","i","باع يَبِيعُ"),
    "وَضَعَ": ("وَضَعَ",("و","ض","ع"),"assimilated","fa3ala","a","وضع يَضَعُ"),
    "سَعَى": ("سَعَى",("س","ع","ى"),"def_yaa","fa3ala","a","سعى يَسْعَى"),
    "رَمَى": ("رَمَى",("ر","م","ى"),"def_yaa","fa3ala","i","رمى يَرْمِي"),
    "غَزَا": ("غَزَا",("غ","ز","ا"),"def_waaw","fa3ala","u","غزا يَغْزُو"),
    "أَخَذَ": ("أَخَذَ",("أ","خ","ذ"),"hamzated","fa3ala","u","أخذ يَأْخُذُ"),
    "شَدَّ": ("شَدَّ",("ش","د","د"),"doubled","fa3ala","u","شدّ يَشُدُّ"),
}
LEXICON = {k: VerbSpec(*v) for k,v in LEXICON.items()}

PFX = {"1s":"أ"+FATHA,"1p":"ن"+FATHA,"2ms":"ت"+FATHA,"2fs":"ت"+FATHA,"2dm":"ت"+FATHA,"2df":"ت"+FATHA,"2mp":"ت"+FATHA,"2fp":"ت"+FATHA,
       "3ms":"ي"+FATHA,"3fs":"ت"+FATHA,"3dm":"ي"+FATHA,"3df":"ت"+FATHA,"3mp":"ي"+FATHA,"3fp":"ي"+FATHA}
INDIC_END = {"3ms": DAMMA, "3fs": DAMMA, "3dm": "ان"+KASRA, "3df": "ان"+KASRA, "3mp": "ون"+FATHA, "3fp": "ْن"+FATHA,
             "2ms": DAMMA, "2fs": "ين"+FATHA, "2dm": "ان"+KASRA, "2df": "ان"+KASRA, "2mp": "ون"+FATHA, "2fp":"ْن"+FATHA,
             "1s":  DAMMA, "1p":  DAMMA}
JUSS_END  = {"3ms": SUKUN, "3fs": SUKUN, "3dm": "ا", "3df": "ا", "3mp": "وا", "3fp": "ْن"+FATHA,
             "2ms": SUKUN, "2fs": "ي", "2dm": "ا", "2df": "ا", "2mp": "وا", "2fp":"ْن"+FATHA,
             "1s":  SUKUN, "1p":  SUKUN}

def _fatha(c): return c+FATHA
def _kasra(c): return c+KASRA
def _damma(c): return c+DAMMA
def _sukun(c): return c+SUKUN

PAST_SUFFIXES = {
    "3ms":"", "3fs":"ت"+SUKUN, "3dm":"ا", "3df":"ا", "3mp":"وا", "3fp":SUKUN+"ن"+FATHA,
    "2ms":SUKUN+"ت"+FATHA, "2fs":SUKUN+"ت"+KASRA, "2dm":SUKUN+"ت"+"ما", "2df":SUKUN+"ت"+"ما",
    "2mp":SUKUN+"ت"+"م"+SUKUN, "2fp":SUKUN+"ت"+"ن"+SHADDA+FATHA, "1s":SUKUN+"ت"+DAMMA, "1p":SUKUN+"ن"+FATHA+"ا",
}

def _past_base_sound(spec:VerbSpec)->str:
    c1,c2,c3=spec.root
    if spec.past_pattern=="fa3ala": return _fatha(c1)+_fatha(c2)+_fatha(c3)
    if spec.past_pattern=="fa3ila": return _fatha(c1)+_kasra(c2)+_fatha(c3)
    if spec.past_pattern=="fa3ula": return _fatha(c1)+_damma(c2)+_fatha(c3)
    return spec.lemma

def _past_hollow(spec:VerbSpec, person:str)->str:
    base3=spec.lemma
    if person in {"3ms","3fs","3dm","3df","3mp"}:
        if person=="3ms": return base3
        if person=="3fs": return base3+PAST_SUFFIXES["3fs"]
        if person in {"3dm","3df"}: return base3+PAST_SUFFIXES["3dm"]
        if person=="3mp": return base3[:-1]+"وا"
    c1,w,c3=spec.root
    short = DAMMA if spec.pres_class=="u" else KASRA
    core = _fatha(c1)+w+short+_sukun(c3)
    return core+{
        "3fp":PAST_SUFFIXES["3fp"],"2ms":PAST_SUFFIXES["2ms"],"2fs":PAST_SUFFIXES["2fs"],
        "2dm":PAST_SUFFIXES["2dm"],"2df":PAST_SUFFIXES["2df"],
        "2mp":PAST_SUFFIXES["2mp"],"2fp":PAST_SUFFIXES["2fp"],
        "1s":PAST_SUFFIXES["1s"],"1p":PAST_SUFFIXES["1p"],
    }[person]

def _past_defective(spec:VerbSpec, person:str)->str:
    if person in {"3ms","3fs","3dm","3df","3mp"}: return spec.lemma+PAST_SUFFIXES[person]
    c1,c2,c3=spec.root
    glide = "ي" if spec.vtype=="def_yaa" else "و"
    base_cv = _fatha(c1)+_fatha(c2)+glide
    forms = {
        "3fp": _fatha(c1)+_fatha(c2)+SUKUN+"ن"+FATHA,
        "2ms": base_cv+PAST_SUFFIXES["2ms"][1:],
        "2fs": base_cv+PAST_SUFFIXES["2fs"][1:],
        "2dm": base_cv+"ما", "2df": base_cv+"ما",
        "2mp": base_cv+"م"+SUKUN, "2fp": base_cv+"ن"+SHADDA+FATHA,
        "1s":  base_cv+DAMMA, "1p":  _fatha(c1)+_fatha(c2)+SUKUN+"ن"+FATHA+"ا",
    }
    return forms[person]

def conjugate_past(spec:VerbSpec)->Dict[str,str]:
    out={}
    if spec.vtype=="hollow":
        for pid,_,_ in PERSONS14:
            out[pid]=_past_hollow(spec,pid)
        return out
    if spec.vtype in {"def_yaa","def_waaw"}:
        for pid,_,_ in PERSONS14:
            out[pid]=_past_defective(spec,pid)
        return out
    stem=_past_base_sound(spec) if spec.past_pattern!="irreg" else spec.lemma
    for pid,_,_ in PERSONS14:
        if pid=="3ms": out[pid]=stem
        else:
            if pid in {"3fp","2ms","2fs","2dm","2df","2mp","2fp","1s","1p"}:
                base = stem[:-1]+SUKUN if stem.endswith(FATHA) else stem+SUKUN
                out[pid]=base+PAST_SUFFIXES[pid]
            else:
                out[pid]=stem+PAST_SUFFIXES[pid]
    return out

def _pres_core_sound(spec:VerbSpec)->str:
    c1,c2,c3=spec.root; v={"a":FATHA,"i":KASRA,"u":DAMMA}[spec.pres_class]
    return _sukun(c1)+c2+v+c3

def _pres_core_hollow(spec:VerbSpec, mood:str, ending:str)->str:
    c1,w,c3=spec.root
    if mood=="jussive" and ending in {SUKUN,""}:
        short=DAMMA if spec.pres_class=="u" else KASRA
        return _sukun(c1)+w+short+_sukun(c3)
    long="و" if spec.pres_class=="u" else "ي"
    return _sukun(c1)+w+long+c3

def _pres_core_defective(spec:VerbSpec, mood:str, person:str)->str:
    c1,c2,c3=spec.root; v={"a":FATHA,"i":KASRA,"u":DAMMA}[spec.pres_class]
    if mood=="jussive" and JUSS_END[person]==SUKUN:
        return _sukun(c1)+c2+v
    glide = "ي" if person=="2fs" else ("و" if person in {"2dm","2df","2mp","3dm","3df","3mp"} else ("ى" if spec.vtype=="def_yaa" else "و"))
    return _sukun(c1)+c2+v+glide

def _pres_core_assimilated(spec:VerbSpec)->str:
    _,c2,c3=spec.root; v={"a":FATHA,"i":KASRA,"u":DAMMA}[spec.pres_class]
    return _sukun(c2)+c3+v

def conjugate_present(spec:VerbSpec, mood:str)->Dict[str,str]:
    END = INDIC_END if mood=="indicative" else JUSS_END
    out={}
    for pid,_,gen in PERSONS14:
        pfx=PFX[pid]; end=END[pid]
        if spec.vtype=="hollow": core=_pres_core_hollow(spec,mood,end)
        elif spec.vtype in {"def_yaa","def_waaw"}: core=_pres_core_defective(spec,mood,pid)
        elif spec.vtype=="assimilated": core=_pres_core_assimilated(spec)
        else: core=_pres_core_sound(spec)
        out[pid]=pfx+core+end
    return out

def _hamzat_wasl(pcls:str)->str: return "ا"+(DAMMA if pcls=="u" else KASRA)

def conjugate_imperative(spec:VerbSpec)->Dict[str,str]:
    out={}
    if spec.vtype=="hollow":
        two_ms="قُلْ" if spec.lemma=="قَالَ" else "بِعْ"
        base="قُول" if spec.lemma=="قَالَ" else "بِيع"
        out["2ms"]=two_ms; out["2fs"]=base+"ي"; out["2dm"]=base+"ا"; out["2df"]=base+"ا"; out["2mp"]=base+"وا"; out["2fp"]="ْنَ"
        return out
    if spec.vtype=="assimilated":
        _,c2,c3=spec.root; core=_fatha(c2)+c3
        out["2ms"]=core+SUKUN; out["2fs"]=core+"ي"; out["2dm"]=core+"ا"; out["2df"]=core+"ا"; out["2mp"]=core+"وا"; out["2fp"]="ْنَ"
        return out
    if spec.vtype in {"def_yaa","def_waaw"}:
        core = "اِرْم" if spec.lemma=="رَمَى" else ("اِسْع" if spec.lemma=="سَعَى" else "اِغْز")
        out["2ms"]= "اِسْعَ" if spec.lemma=="سَعَى" else ("اِرْمِ"+SUKUN if spec.lemma=="رَمَى" else "اِغْزُ"+SUKUN)
        out["2fs"]=core+"ي"; out["2dm"]=core+"ا"; out["2df"]=core+"ا"; out["2mp"]=core+"وا"; out["2fp"]="ْنَ"
        return out
    c1,c2,c3=spec.root; hw=_hamzat_wasl(spec.pres_class); mid={"a":FATHA,"i":KASRA,"u":DAMMA}[spec.pres_class]
    base=hw+_sukun(c1)+c2+mid+_sukun(c3); core=hw+_sukun(c1)+c2+mid+c3
    out["2ms"]=base; out["2fs"]=core+"ي"; out["2dm"]=core+"ا"; out["2df"]=core+"ا"; out["2mp"]=core+"وا"; out["2fp"]="ْنَ"
    return out

def rows_for(spec:VerbSpec)->List[Dict[str,str]]:
    rows=[]
    past=conjugate_past(spec); pres=conjugate_present(spec,"indicative"); juss=conjugate_present(spec,"jussive"); imp=conjugate_imperative(spec)
    for pid,num,gen in PERSONS14:
        rows.append({"lemma":spec.lemma,"root":"".join(spec.root),"type":spec.vtype,"set":"past","person":pid,"number":num,"gender":gen,"form":past[pid]})
        rows.append({"lemma":spec.lemma,"root":"".join(spec.root),"type":spec.vtype,"set":"present_indic","person":pid,"number":num,"gender":gen,"form":pres[pid]})
        rows.append({"lemma":spec.lemma,"root":"".join(spec.root),"type":spec.vtype,"set":"present_juss","person":pid,"number":num,"gender":gen,"form":juss[pid]})
    for pid in ["2ms","2fs","2dm","2df","2mp","2fp"]:
        rows.append({"lemma":spec.lemma,"root":"".join(spec.root),"type":spec.vtype,"set":"imperative",
                     "person":pid,"number":{"2ms":"sg","2fs":"sg","2dm":"du","2df":"du","2mp":"pl","2fp":"pl"}[pid],
                     "gender":{"2ms":"m","2fs":"f","2dm":"m","2df":"f","2mp":"m","2fp":"f"}[pid],"form":imp[pid]})
    return rows

def export_csv(path:str, rows:List[Dict[str,str]])->None:
    cols=["lemma","root","type","set","person","number","gender","form"]
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)

def sample_specs()->List[VerbSpec]:
    keys=["كَتَبَ","قَرَأَ","دَخَلَ","جَلَسَ","عَلِمَ","حَسُنَ","قَالَ","بَاعَ","وَضَعَ","سَعَى","رَمَى","غَزَا","أَخَذَ","شَدَّ"]
    return [LEXICON[k] for k in keys]

def main()->None:
    ap=argparse.ArgumentParser(description="Vocalized Form I engine (14 forms × past/pres/juss/imp)")
    ap.add_argument("--sample-csv", type=str, default="", help="export CSV for 14 sample verbs")
    ap.add_argument("--lemma", type=str, default="", help="export CSV for a specific lemma in lexicon")
    ap.add_argument("--csv", type=str, default="", help="output CSV path when --lemma is used")
    args=ap.parse_args()

    if args.sample_csv:
        rows=[]
        for s in sample_specs():
            rows+=rows_for(s)
        export_csv(args.sample_csv, rows)
        print(f"Exported {len(rows)} rows to {args.sample_csv}")
        return

    if args.lemma and args.csv:
        spec = LEXICON.get(args.lemma)
        if not spec:
            raise SystemExit("Lemma not in lexicon")
        rows = rows_for(spec)
        export_csv(args.csv, rows)
        print(f"Exported {len(rows)} rows to {args.csv}")
        return

    ap.print_help()

if __name__=="__main__":
    main()
