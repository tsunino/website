# -*- coding: utf-8 -*-
"""
Konversi dashboard Flask -> situs statis untuk GitHub Pages (Python berjalan di browser via Pyodide).
Pemakaian:  python build_github.py dashboard_uts_bi_p8.py
Hasil    :  folder docs/ berisi index.html (unggah ke GitHub, aktifkan Pages).
Kode analisis (EDA, preprocessing, Apriori, K-Means, rekomendasi) dan antarmuka dashboard
diambil APA ADANYA dari file asli; hanya lapisan Flask yang diganti.
"""
import ast, os, re, sys

src_path = sys.argv[1] if len(sys.argv) > 1 else "dashboard_uts_bi_p8.py"
src = open(src_path, encoding="utf-8").read()

def mark(s, key):
    assert key in s, f"Penanda '{key}' tidak ditemukan - pastikan memakai file dashboard asli."
    return s.index(key)

# --- ambil string CSS & APP (HTML+JS dashboard) dari file asli
vals = {}
for n in ast.parse(src).body:
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("CSS", "APP"):
        vals[n.targets[0].id] = ast.literal_eval(n.value)
CSS, APP = vals["CSS"], vals["APP"]
layout = APP[:APP.index("<script src")]
js = APP[APP.index("<script>") + 8:APP.rindex("</script>")]

old_j = "async function J(u){const r=await fetch(u);return r.json()}"
assert old_j in js, "Fungsi J() tidak ditemukan di JavaScript asli."
js = js.replace(old_j, "async function J(u){const [p,q]=u.split('?');const o={};new URLSearchParams(q||'').forEach((v,k)=>{o[k]=v});return JSON.parse(await PY(p,o))}")

# --- ambil kode analisis Python, buang lapisan Flask
head = src[:mark(src, "# ------------------------------------------------------------------ halaman")]
tail = src[mark(src, "def guard():"):mark(src, "if __name__")]
head = "\n".join(l for l in head.split("\n") if not re.match(r"\s*(from flask import|BASE\s*=|app\s*=\s*Flask|app\.secret_key|app\.config)", l))

stubs = '''
# ---- pengganti Flask (berjalan di browser lewat Pyodide)
class _App:
    def __init__(s): s.routes = {}
    def route(s, p, **k):
        def d(f): s.routes[p] = f; return f
        return d
class _Req: args = {}
app = _App(); request = _Req(); session = {'ok': True}
def Response(body, mimetype=None, headers=None): return body
def redirect(x): return ""
def send_file(x): return ""
def logged(): return True
'''
glue = '''
def process(b, name):
    try:
        raw, prod, cust = load(io.BytesIO(bytes(b.to_py())))
        S.clear()
        S['fname'], S['raw_n'] = name, len(raw)
        S['audit'] = audit(raw, prod)
        clean, log, ba = preprocess(raw, prod, cust)
        S['clean'], S['log'], S['ba'] = clean, log, ba
        S['tx'], S['rfm'], S['ref'] = build(clean)
        S['Z'], S['ev'] = km_eval(S['rfm'])
        km_fit(K_DEF)
        return ""
    except Exception as e:
        S.clear()
        return str(e)

def handle(path, qs):
    request.args = json.loads(qs)
    if path.startswith('/download/'): return dl(path.split('/')[-1])
    return app.routes[path]()
'''
core = (head + stubs + tail + glue).replace("</script", "<\\/script")
compile(core, "core", "exec")  # cek sintaks

TEMPLATE = r'''<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UTS Business Intelligence - Febriana Tsunino</title><style>__CSS__</style>
</head><body>
<div id="screen"></div>
<script type="text/plain" id="core-py">__CORE__</script>
<script type="text/plain" id="app-js">__JS__</script>
<script type="text/plain" id="app-html">__LAYOUT__</script>
<script>
const NAMA="Febriana Tsunino",NPM="51230136",UNIV="Universitas Timor",KODE="TIF46212",PRODI="Teknologi Informasi",SEM="VII (Tujuh)",
DOSEN="Krisantus Jumarto Tey Seran, S.T., M.T.",USER="febriana",PWD="51230136";
let PYO=null,STAT='Memuat mesin Python (Pyodide)...',FNAME='';
const scr=document.getElementById('screen'),tick=()=>new Promise(r=>setTimeout(r,40));
const loadJS=async us=>{for(const u of us){try{await new Promise((ok,no)=>{const e=document.createElement('script');e.src=u;e.onload=ok;e.onerror=no;document.head.appendChild(e)});return}catch(e){}}throw new Error('tidak bisa memuat '+us[0])};
const chartP=loadJS(['https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js','https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js','https://gcore.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js']);chartP.catch(()=>{});
function setStat(t){STAT=t;const e=document.getElementById('pst');if(e)e.textContent=t}
const readyP=(async()=>{await loadJS(['https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js','https://gcore.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js','https://fastly.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js']);PYO=await loadPyodide();setStat('Memuat pandas, scikit-learn, openpyxl (±1 menit saat pertama kali)...');
await PYO.loadPackage(['numpy','pandas','scikit-learn','openpyxl']);await PYO.runPythonAsync(document.getElementById('core-py').textContent);setStat('Mesin analisis siap.')})();
readyP.catch(e=>setStat('Gagal memuat mesin Python: '+e));
async function PY(p,o){await readyP;await tick();return PYO.globals.get('handle')(p,JSON.stringify(o))}
async function download(n){const t=await PY('/download/'+n,{});const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([t],{type:'text/csv'}));a.download=n;a.click()}
document.addEventListener('click',e=>{const a=e.target.closest('a[href^="/download/"],a[href="/upload"]');if(!a)return;e.preventDefault();const h=a.getAttribute('href');h=='/upload'?showUpload():download(h.split('/').pop())});
function topbar(extra){return '<div class="top"><b>📊 UTS Business Intelligence · '+NAMA+' ('+NPM+') · '+UNIV+'</b><span>'+extra+'<a href="#" onclick="showCover();return false">Keluar</a></span></div>'}
function showCover(err){const ini=NAMA.split(' ').slice(0,2).map(w=>w[0]).join('');
scr.innerHTML='<div class="cover"><div class="left"><img class="foto" src="foto.jpg" onerror="this.outerHTML=\'<div class=foto>'+ini+'</div>\'">'+
'<div><span class="pill">UJIAN TENGAH SEMESTER</span><span class="pill">'+KODE+'</span></div><h1>Business <span>Intelligence</span><br>Dashboard</h1>'+
'<div style="font-size:17px;opacity:.95">Integrasi Data Mining &amp; Business Intelligence pada Data Transaksi Toko</div>'+
'<table class="id"><tr><td>Nama</td><td><b>: '+NAMA+'</b></td></tr><tr><td>NPM</td><td><b>: '+NPM+'</b></td></tr><tr><td>Universitas</td><td><b>: '+UNIV+'</b></td></tr><tr><td>Program Studi</td><td>: '+PRODI+'</td></tr><tr><td>Semester</td><td>: '+SEM+'</td></tr><tr><td>Dosen</td><td>: '+DOSEN+'</td></tr></table>'+
'<div style="font-size:13px;opacity:.85">EDA · Preprocessing · Apriori · K-Means · Dashboard BI</div></div>'+
'<div class="right"><form class="box" onsubmit="return doLogin(this)"><h2>Masuk</h2><label>Username</label><input name="u" required autofocus><label>Kata sandi</label><input name="p" type="password" required><div class="err">'+(err||'')+'</div><br><button class="btn" style="width:100%">Masuk →</button></form></div></div>'}
function doLogin(f){if(f.u.value.trim().toLowerCase()==USER&&f.p.value==PWD)showUpload();else showCover('Username atau kata sandi salah.');return false}
function showUpload(msg){scr.innerHTML=topbar('')+'<div class="wrap"><div class="card"><h2>Unggah File Data</h2><p>Unggah file Excel <b>P8__UTS_Business_Intelligence.xlsx</b> (sheet <i>Data_Raw</i>, <i>Data_Produk</i>, <i>Data_Pelanggan</i>). File diproses di browser Anda dan tidak dikirim ke server mana pun.</p>'+
(FNAME?'<div class="note">File aktif: <b>'+FNAME+'</b>. <a href="#" onclick="showApp();return false">Buka dashboard →</a></div>':'')+
'<div class="note" id="pst">'+STAT+'</div><form onsubmit="doUpload(this);return false"><input type="file" name="f" accept=".xlsx,.xlsm" required><div class="err">'+(msg||'')+'</div><br><button id="b" class="btn o">Unggah &amp; Analisis</button></form></div></div>'}
async function doUpload(f){const file=f.f.files[0],b=document.getElementById('b');b.disabled=true;b.textContent='Memproses... mohon tunggu';
try{await readyP;await tick();const buf=new Uint8Array(await file.arrayBuffer());const err=PYO.globals.get('process')(buf,file.name);
if(err){b.disabled=false;return showUpload('Gagal memproses file: '+err)}FNAME=file.name;showApp()}catch(e){showUpload('Gagal: '+e)}return false}
async function showApp(){try{await chartP}catch(e){alert('Gagal memuat Chart.js (grafik). Periksa koneksi internet lalu muat ulang.');return}scr.innerHTML=topbar("<span style='margin-right:14px;font-size:13px'>File: "+FNAME+"</span>")+document.getElementById('app-html').textContent;(0,eval)(document.getElementById('app-js').textContent)}
showCover();
</script></body></html>'''

out = (TEMPLATE.replace("__CSS__", CSS).replace("__CORE__", core)
       .replace("__JS__", js.replace("</script", "<\\/script")).replace("__LAYOUT__", layout))
os.makedirs("docs", exist_ok=True)
open("docs/index.html", "w", encoding="utf-8").write(out)
open("docs/.nojekyll", "w").close()
print(f"OK -> docs/index.html ({len(out)//1024} KB). Unggah folder docs/ ke GitHub lalu aktifkan Pages.")
