"""BookMart - single-file Streamlit frontend for the Kitaab Exchange FastAPI backend.

Real backend endpoints used (nothing else exists):
  GET   /books/?title=&author=   public, returns UNSOLD books only
  POST  /books/                  x-api-key, body {title, author, price:int, user_id}
  PATCH /books/{id}/sold         x-api-key, marks a book as sold
  GET   /users/                  public
  POST  /users/                  x-api-key, body {name, email, college}
"""
import os
from html import escape

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("API_KEY", "secret123")  # must match API_KEY in auth.py

st.set_page_config(page_title="DU BookMart", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--navy:#0B1F3A;--blue:#1D4ED8;--bg:#F5F7FB;--text:#0F172A;--muted:#64748B;--line:#E2E8F0;
--shadow:0 1px 2px rgba(15,23,42,.05),0 8px 22px rgba(15,23,42,.07)}
html,body,.stApp,button,input,textarea{font-family:'Inter',system-ui,sans-serif}
.stApp{background:var(--bg);color:var(--text)}
#MainMenu,footer,.stDeployButton{display:none!important}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1160px;padding:1rem 1.25rem 4rem}
[data-testid="stWidgetLabel"] p,label,[data-testid="stMetricLabel"] *,[data-testid="stCaptionContainer"]{color:#334155!important}
input,textarea,[data-baseweb="select"]>div{background:#fff!important;color:var(--text)!important;border-radius:10px!important}

/* navbar */
.st-key-nav{background:#fff;border:1px solid var(--line);border-radius:16px;padding:.7rem 1rem;box-shadow:var(--shadow);margin-bottom:1.2rem}
.brand{display:flex;align-items:center;gap:.7rem}
.logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,var(--navy),var(--blue));color:#fff;font-weight:800;display:grid;place-items:center;letter-spacing:.02em}
.bname{font-size:1.2rem;font-weight:800;color:var(--navy);line-height:1.1}
.btag{font-size:.78rem;color:var(--muted)}

/* buttons */
.stApp .stButton>button,.stApp .stFormSubmitButton>button{width:100%;border-radius:10px;font-weight:600;padding:.5rem .9rem;transition:none}
.stApp button[kind^="primary"],.stApp [data-testid^="stBaseButton-primary"]{background:var(--navy)!important;border:1px solid var(--navy)!important;color:#fff!important}
.stApp button[kind^="primary"]:hover,.stApp [data-testid^="stBaseButton-primary"]:hover{background:var(--blue)!important;border-color:var(--blue)!important}
.stApp button[kind^="secondary"],.stApp [data-testid^="stBaseButton-secondary"]{background:#fff!important;border:1px solid var(--line)!important;color:var(--navy)!important}
.stApp button[kind^="secondary"]:hover,.stApp [data-testid^="stBaseButton-secondary"]:hover{border-color:var(--blue)!important;color:var(--blue)!important}

/* hero */
.hero{background:linear-gradient(135deg,var(--navy),#1E3A8A);border-radius:20px;padding:2.8rem 2.2rem;box-shadow:0 12px 30px rgba(11,31,58,.25);margin-bottom:1rem}
.hero h1{color:#fff!important;font-size:2.4rem;font-weight:800;margin:0 0 .5rem;padding:0;line-height:1.15}
.hero p{color:#CBD5E1!important;font-size:1.05rem;margin:0}

/* cards and forms */
div[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stForm"]{background:#fff;border:1px solid var(--line)!important;border-radius:16px;box-shadow:var(--shadow)}
[data-testid="stForm"]{padding:1.4rem}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:.9rem 1.1rem;box-shadow:var(--shadow)}
[data-testid="stMetricValue"]{color:var(--navy);font-weight:800}
.h2{font-size:1.65rem;font-weight:800;color:var(--navy);margin:.3rem 0 .1rem}
.sub{color:var(--muted);margin:0 0 1rem}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:.6rem}
.pill{font-size:.74rem;font-weight:700;padding:.2rem .65rem;border-radius:999px}
.pill.ok{background:#DCFCE7;color:#166534}.pill.sold{background:#FEE2E2;color:#991B1B}
.bid{color:var(--muted);font-size:.8rem}
.t{font-size:1.06rem;font-weight:700;color:var(--navy);line-height:1.3}
.a{color:var(--muted);font-size:.9rem;margin:.15rem 0 .4rem}
.p{font-size:1.55rem;font-weight:800;color:var(--blue);margin:.2rem 0}
.s{color:#475569;font-size:.84rem;margin-bottom:.6rem}
.fact{display:flex;justify-content:space-between;padding:.7rem 0;border-top:1px solid var(--line)}
.fact span{color:var(--muted)}.fact b{color:var(--navy)}
@media(max-width:640px){.hero{padding:1.8rem 1.2rem}.hero h1{font-size:1.7rem}}
</style>""", unsafe_allow_html=True)

ss = st.session_state
for k, v in {"page": "Home", "q": "", "book": None, "uid": None, "sold": {}, "flash": None}.items():
    ss.setdefault(k, v)


# ------------------------------------------------------------- API layer ----
def call(method, path, **kw):
    """Returns (data, error_message). Never raises, never shows tracebacks."""
    try:
        r = requests.request(method, API_URL + path, headers={"X-API-Key": API_KEY}, timeout=8, **kw)
    except requests.exceptions.ConnectionError:
        return None, f"Cannot reach the server at {API_URL}. Please make sure the FastAPI backend is running."
    except requests.exceptions.RequestException:
        return None, "The server took too long to respond. Please try again."
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail")
        except (ValueError, AttributeError):
            detail = None
        detail = detail if isinstance(detail, str) else None
        if r.status_code == 401:
            return None, "Authentication failed. Please check your API key."
        if r.status_code == 404:
            return None, detail or "The requested item was not found."
        if r.status_code == 422:
            return None, "Please check the information you entered."
        if r.status_code >= 500:
            return None, "Something went wrong on the server. Please try again later."
        return None, detail or "The request could not be processed."
    try:
        return r.json(), None
    except ValueError:
        return None, "The server sent an unexpected response."


def load(path, **kw):
    data, err = call("GET", path, **kw)
    if err:
        st.error(err)
        st.stop()
    return data


def search_books(q, field):
    """Backend ANDs title+author filters, so 'both' is two calls merged client-side."""
    if not q:
        return load("/books/")
    found = {}
    if field != "Author":
        found.update({b["id"]: b for b in load("/books/", params={"title": q})})
    if field != "Title":
        found.update({b["id"]: b for b in load("/books/", params={"author": q})})
    return list(found.values())


# ------------------------------------------------------------- UI helpers ----
def go(page, **state):
    ss.page = page
    ss.update(state)


def esc(x):
    return escape(str(x))


def head(title, sub):
    st.markdown(f'<div class="h2">{title}</div><p class="sub">{sub}</p>', unsafe_allow_html=True)


def pill(b):
    return '<span class="pill sold">Sold</span>' if b["is_sold"] else '<span class="pill ok">Available</span>'


def seller_name(users, uid):
    u = users.get(uid)
    return f"{esc(u['name'])}, {esc(u['college'])}" if u else f"Seller #{uid}"


def card(b, users, key, details=True):
    with st.container(border=True):
        st.markdown(
            f'<div class="top">{pill(b)}<span class="bid">#{b["id"]}</span></div>'
            f'<div class="t">{esc(b["title"])}</div><div class="a">by {esc(b["author"])}</div>'
            f'<div class="p">₹{b["price"]:,}</div><div class="s">Seller: {seller_name(users, b["user_id"])}</div>',
            unsafe_allow_html=True)
        if details:
            st.button("View Details", key=f"{key}_{b['id']}", on_click=go, args=("Book Details",),
                      kwargs={"book": b["id"]})


def grid(books, users, key):
    for i in range(0, len(books), 3):
        for col, b in zip(st.columns(3), books[i:i + 3]):
            with col:
                card(b, users, key)


def user_id_input():
    uid = st.number_input("Your User ID", min_value=1, step=1, value=ss.uid or 1,
                          help="Shown after registration. The API has no login, so the ID identifies the seller.")
    ss.uid = int(uid)
    return ss.uid


def mark_sold(b):
    _, err = call("PATCH", f"/books/{b['id']}/sold")
    if err:
        ss.flash = ("error", err)
    else:
        ss.sold[b["id"]] = {**b, "is_sold": True}
        ss.flash = ("success", f"“{b['title']}” was marked as sold.")


# ----------------------------------------------------------------- pages ----
def home():
    books, users = load("/books/"), load("/users/")
    st.markdown('<div class="hero"><h1>Buy &amp; Sell Used Textbooks</h1>'
                '<p>Affordable textbooks from fellow Delhi University students.</p></div>', unsafe_allow_html=True)
    with st.form("hero_search"):
        c1, c2 = st.columns([5, 1])
        q = c1.text_input("Search", placeholder="Search by title or author", label_visibility="collapsed")
        if c2.form_submit_button("Search", type="primary"):
            go("Browse Books", q=q.strip())
            st.rerun()
    b1, b2, _ = st.columns([1.2, 1.2, 3])
    b1.button("Browse Books", type="primary", key="h1", on_click=go, args=("Browse Books",), kwargs={"q": ""})
    b2.button("Sell Your Book", key="h2", on_click=go, args=("Sell a Book",))
    st.write("")
    m1, m2, m3 = st.columns(3)
    m1.metric("Available Books", len(books))
    m2.metric("Sold This Session", len(ss.sold))
    m3.metric("Registered Students", len(users))
    st.caption("The backend only lists unsold books, so overall sold and total counts are not available from the API.")


def browse():
    head("Browse Books", "Available used textbooks from Delhi University students.")
    c1, c2 = st.columns([4, 1.5])
    q = c1.text_input("Search", value=ss.q, placeholder="Search by title or author").strip()
    field = c2.selectbox("Search in", ["Title & author", "Title", "Author"])
    books = sorted(search_books(q, field), key=lambda b: -b["id"])
    users = {u["id"]: u for u in load("/users/")}
    st.caption(f"{len(books)} available book(s)")
    if not books:
        st.info("No books match your search.")
    grid(books, users, "br")


def details():
    st.button("Back to Browse", on_click=go, args=("Browse Books",))
    b = next((x for x in load("/books/") if x["id"] == ss.book), None) or ss.sold.get(ss.book)
    if not b:
        st.warning("This book is no longer available. It may have been sold.")
        return
    users = {u["id"]: u for u in load("/users/")}
    u = users.get(b["user_id"], {})
    left, right = st.columns([2, 1])
    with left, st.container(border=True):
        facts = [("Book ID", f"#{b['id']}"), ("Seller", esc(u.get("name", f"User #{b['user_id']}"))),
                 ("College", esc(u.get("college", "-")))]
        st.markdown(f'{pill(b)}<div class="h2" style="margin-top:.7rem">{esc(b["title"])}</div>'
                    f'<p class="sub">by {esc(b["author"])}</p><div class="p" style="font-size:2.2rem">₹{b["price"]:,}</div>'
                    + "".join(f'<div class="fact"><span>{k}</span><b>{v}</b></div>' for k, v in facts),
                    unsafe_allow_html=True)
    with right, st.container(border=True):
        st.markdown('<div class="t">Interested in this book?</div><p class="sub">'
                    'Contact/transaction functionality can be added in a future version.</p>', unsafe_allow_html=True)


def sell():
    head("Sell a Book", "List a used textbook for other students.")
    with st.form("sell"):
        title = st.text_input("Title *", max_chars=150)
        author = st.text_input("Author *", max_chars=100)
        c1, c2 = st.columns(2)
        price = c1.number_input("Price (₹) *", min_value=0, max_value=100000, step=10, value=0)
        uid = c2.number_input("Seller User ID *", min_value=1, step=1, value=ss.uid or 1)
        submitted = st.form_submit_button("List Book", type="primary")
    if not submitted:
        return
    errors = [m for ok, m in [(title.strip(), "Title is required."), (author.strip(), "Author is required."),
                              (price > 0, "Price must be a whole number greater than 0.")] if not ok]
    if errors:
        for m in errors:
            st.error(m)
        return
    if int(uid) not in {u["id"] for u in load("/users/")}:
        st.error(f"No user with ID {int(uid)} exists. Please register first.")
        return
    book, err = call("POST", "/books/", json={"title": title.strip(), "author": author.strip(),
                                              "price": int(price), "user_id": int(uid)})
    if err:
        st.error(err)
        return
    ss.uid = int(uid)
    st.success("Book listed successfully!")
    card(book, {u["id"]: u for u in load("/users/")}, "new", details=False)
    st.button("View marketplace", on_click=go, args=("Browse Books",), kwargs={"q": ""})


def my_books():
    head("My Books", "Manage your listings.")
    uid = user_id_input()
    users = {u["id"]: u for u in load("/users/")}
    if uid not in users:
        st.warning("No user found with this ID. Register first or enter your correct ID.")
        return
    st.markdown(f'<p class="sub">Seller: <b>{esc(users[uid]["name"])}</b>, {esc(users[uid]["college"])}</p>',
                unsafe_allow_html=True)
    mine = [b for b in load("/books/") if b["user_id"] == uid]
    sold = [b for b in ss.sold.values() if b["user_id"] == uid]
    if not mine and not sold:
        st.info("You have no listings yet.")
    for b in mine:
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 1.5, 1.5], vertical_alignment="center")
            c1.markdown(f'<div class="t">{esc(b["title"])}</div><div class="a" style="margin:0">'
                        f'by {esc(b["author"])} · #{b["id"]}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="t">₹{b["price"]:,}</div>{pill(b)}', unsafe_allow_html=True)
            c3.button("Mark as Sold", key=f"sold_{b['id']}", type="primary", on_click=mark_sold, args=(b,))
    if sold:
        st.markdown('<p class="sub" style="margin-top:1rem">Sold this session (the API lists unsold books only)</p>',
                    unsafe_allow_html=True)
        grid(sold, users, "sd")


def register():
    head("Register", "Create your seller account.")
    with st.form("register"):
        name = st.text_input("Full name *", max_chars=80)
        email = st.text_input("Email *")
        college = st.text_input("College *", placeholder="e.g. Hansraj College")
        submitted = st.form_submit_button("Create Account", type="primary")
    if not submitted:
        return
    e = email.strip()
    errors = [m for ok, m in [(name.strip(), "Name is required."),
                              ("@" in e and "." in e.split("@")[-1], "Please enter a valid email address."),
                              (college.strip(), "College is required.")] if not ok]
    if errors:
        for m in errors:
            st.error(m)
        return
    user, err = call("POST", "/users/", json={"name": name.strip(), "email": e, "college": college.strip()})
    if err:
        st.error(err)
        return
    ss.uid = user["id"]
    st.success("Account created successfully!")
    with st.container(border=True):
        st.markdown("".join(f'<div class="fact"><span>{k}</span><b>{esc(v)}</b></div>' for k, v in
                            [("User ID", user["id"]), ("Name", user["name"]), ("Email", user["email"]),
                             ("College", user["college"])]), unsafe_allow_html=True)
    st.button("Sell a Book", type="primary", on_click=go, args=("Sell a Book",))


# ------------------------------------------------------------------ main ----
NAV = ["Home", "Browse Books", "Sell a Book", "My Books", "Register"]
with st.container(key="nav"):
    cols = st.columns([2.4, 1, 1.3, 1.1, 1, 1.1])
    cols[0].markdown('<div class="brand"><div class="logo">DU</div><div><div class="bname">DU BookMart</div>'
                     '<div class="btag">Buy &amp; Sell Used Textbooks</div></div></div>', unsafe_allow_html=True)
    for col, p in zip(cols[1:], NAV):
        col.button(p, key=f"nav_{p}", on_click=go, args=(p,), type="primary" if ss.page == p else "secondary")

if ss.flash:
    kind, msg = ss.flash
    ss.flash = None
    (st.success if kind == "success" else st.error)(msg)

{"Home": home, "Browse Books": browse, "Book Details": details, "Sell a Book": sell,
 "My Books": my_books, "Register": register}.get(ss.page, home)()
