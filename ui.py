import streamlit as st

PAGE_CSS = r'''
<style>
:root{--navy:#0f172a;--slate:#334155;--muted:#64748b;--line:#e2e8f0;--bg:#f8fafc;--blue:#2563eb;--blue2:#1d4ed8;--green:#059669;--amber:#d97706;--red:#dc2626;}
.stApp{background:var(--bg);color:var(--navy);}
.block-container{padding-top:1.35rem;padding-bottom:2.5rem;max-width:1480px;}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line);}
[data-testid="stSidebar"]>div:first-child{padding-top:1rem;}
.brand{padding:18px 17px;border-radius:16px;background:linear-gradient(135deg,#0f172a,#1e3a8a);color:#fff;margin:0 0 18px;box-shadow:0 12px 30px rgba(15,23,42,.12)}
.brand .brand-mark{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#bfdbfe;font-weight:700}
.brand h1{font-size:1.12rem;margin:4px 0 2px;letter-spacing:.03em}
.brand p{margin:0;color:#cbd5e1;font-size:.76rem}
.user-card{padding:12px 13px;border:1px solid var(--line);border-radius:13px;background:#f8fafc;margin-bottom:14px}
.user-card .name{font-weight:700;font-size:.9rem}.user-card .role{font-size:.74rem;color:var(--muted);margin-top:2px}
.hero{padding:25px 28px;border-radius:20px;background:linear-gradient(135deg,#0f172a 0%,#172554 54%,#1d4ed8 100%);color:#fff;margin-bottom:20px;box-shadow:0 16px 35px rgba(15,23,42,.12);position:relative;overflow:hidden}
.hero:after{content:"";position:absolute;width:240px;height:240px;border-radius:50%;right:-85px;top:-120px;background:rgba(255,255,255,.07)}
.hero .eyebrow{font-size:.72rem;text-transform:uppercase;letter-spacing:.13em;color:#bfdbfe;font-weight:700;margin-bottom:6px}
.hero h1{margin:0;font-size:1.85rem;line-height:1.2;position:relative;z-index:1}.hero p{margin:.55rem 0 0;color:#dbeafe;font-size:.9rem;position:relative;z-index:1}
.kpi{padding:18px 19px;background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 5px 18px rgba(15,23,42,.045);min-height:112px}
.kpi .label{font-size:.72rem;color:var(--muted);font-weight:750;text-transform:uppercase;letter-spacing:.06em}.kpi .value{font-size:1.5rem;font-weight:800;color:var(--navy);margin-top:7px}.kpi .sub{font-size:.73rem;color:#94a3b8;margin-top:4px}
.section-title{font-size:1.02rem;font-weight:800;color:var(--navy);margin:22px 0 10px}.section-note{font-size:.78rem;color:var(--muted);margin:-5px 0 12px}
.panel{background:#fff;border:1px solid var(--line);border-radius:16px;padding:17px 18px;box-shadow:0 4px 16px rgba(15,23,42,.035)}
.insight{border-left:4px solid var(--blue);background:#eff6ff;padding:13px 15px;border-radius:0 12px 12px 0;color:#1e3a8a;font-size:.82rem}
.success-box{border-left:4px solid var(--green);background:#ecfdf5;padding:13px 15px;border-radius:0 12px 12px 0;color:#065f46;font-size:.82rem}
.warn-box{border-left:4px solid var(--amber);background:#fffbeb;padding:13px 15px;border-radius:0 12px 12px 0;color:#92400e;font-size:.82rem}
.login-shell{max-width:470px;margin:6vh auto 0}.login-card{padding:32px;background:#fff;border:1px solid var(--line);border-radius:22px;box-shadow:0 20px 60px rgba(15,23,42,.11)}
.login-brand{text-align:center}.login-brand .mark{font-size:.72rem;letter-spacing:.15em;color:#2563eb;font-weight:800}.login-brand h1{font-size:1.65rem;margin:7px 0 2px}.login-brand p{color:var(--muted);font-size:.82rem;margin:0 0 22px}
.footer{text-align:center;color:#94a3b8;font-size:.7rem;margin-top:25px}.mini-badge{display:inline-block;padding:4px 9px;border-radius:999px;background:#eff6ff;color:#1d4ed8;font-size:.7rem;font-weight:750}
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:12px 14px;border-radius:14px}
.stButton>button{border-radius:10px;font-weight:650}.stDownloadButton>button{border-radius:10px}.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"],.stMultiSelect div[data-baseweb="select"]{border-radius:10px}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden;border:1px solid var(--line)}
hr{border-color:var(--line)}
</style>
'''

def setup():
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

def hero(title, subtitle, eyebrow='PT Kramat Motor • Business Intelligence'):
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def kpi(label, value, sub=''):
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)

def section(title, note=''):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)

def panel_start():
    st.markdown('<div class="panel">', unsafe_allow_html=True)

def panel_end():
    st.markdown('</div>', unsafe_allow_html=True)
