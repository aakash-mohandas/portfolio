#!/usr/bin/env python3
"""Generate 1200x630 Open Graph images for the portfolio site."""
import glob, json, os, re, subprocess, sys

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = "/private/var/folders/5j/jp6xf48d3bq41z28vg7qh5m80000gn/T/opencode/og"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE = "aakash-mohandas.github.io/portfolio"

BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden;background:#0B0C0E;color:#ECEEF1;
 font-family:"Instrument Sans",system-ui,sans-serif}
.frame{position:relative;width:1200px;height:630px;padding:64px 72px;display:flex;flex-direction:column;
 background:
  radial-gradient(900px 500px at 88% -12%, rgba(91,79,224,.30), transparent 62%),
  radial-gradient(700px 420px at -8% 108%, rgba(214,180,120,.14), transparent 60%),
  #0B0C0E;overflow:hidden}
.grid{position:absolute;inset:0;opacity:.5;
 background-image:linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px),
  linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px);
 background-size:60px 60px}
.top{display:flex;align-items:center;gap:16px;position:relative;z-index:2}
.av{width:58px;height:58px;border-radius:50%;background:#ECEEF1;color:#0B0C0E;
 display:grid;place-items:center;font:800 22px "Inter Tight",sans-serif;letter-spacing:-.5px}
.name{font:600 21px "Instrument Sans",sans-serif;letter-spacing:.01em}
.name span{display:block;font-size:14px;font-weight:400;color:#98A0AA;letter-spacing:.06em;
 text-transform:uppercase;margin-top:2px}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;position:relative;z-index:2;padding:10px 0}
.tag{align-self:flex-start;font:700 13px/1 "Inter Tight",sans-serif;letter-spacing:.14em;
 text-transform:uppercase;color:#B4ACFF;background:rgba(91,79,224,.18);
 border:1px solid rgba(141,130,255,.32);border-radius:99px;padding:9px 16px;margin-bottom:26px}
h1{font:800 60px/1.12 "Inter Tight",sans-serif;letter-spacing:-.025em;max-width:1020px}
h1.md{font-size:52px}
h1.sm{font-size:45px}
h1.xs{font-size:39px}
.sub{margin-top:22px;font-size:23px;color:#98A0AA;line-height:1.5;max-width:900px}
.foot{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;
 border-top:1px solid rgba(255,255,255,.09);padding-top:22px;font-size:17px;color:#7D848D}
.foot b{color:#C9CFD6;font-weight:600}
"""


def page(inner):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&family=Inter+Tight:wght@700;800&display=swap">
<style>{BASE_CSS}</style></head><body><div class="frame"><div class="grid"></div>{inner}</div></body></html>"""


def top():
    return ('<div class="top"><div class="av">AM</div>'
            '<div class="name">Aakash Mohandas<span>Cloud &amp; DevOps Engineer</span></div></div>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


def size_class(t):
    n = len(t)
    if n < 46:
        return ""
    if n < 60:
        return "md"
    if n < 74:
        return "sm"
    return "xs"


def build_site():
    return page(top() + """
<div class="body">
  <h1>Infrastructure,<br>written down.</h1>
  <p class="sub">13+ years automating cloud platforms. Notes on Terraform, Vault,
  Kubernetes and Go — plus the occasional detour into AI tooling.</p>
</div>""" + foot(SITE, "Portfolio &amp; Blog"))


def build_post(title, tag, date, read):
    return page(top() + f"""
<div class="body">
  <div class="tag">{tag}</div>
  <h1 class="{size_class(title)}">{title}</h1>
</div>""" + foot(SITE, f"{date} &middot; {read}"))


def main():
    os.makedirs(TMP, exist_ok=True)
    jobs = [("og.png", build_site())]

    for f in sorted(glob.glob("blogs/posts/*.html")):
        s = open(f).read()
        title = re.search(r"<h1>(.*?)</h1>", s, re.S).group(1)
        title = re.sub(r"<[^>]+>", "", title).strip()
        tag = re.search(r'<span class="tag">([^<]+)</span>', s).group(1)
        date = re.search(r'<span class="date">([^<]+)</span>', s).group(1)
        read = re.search(r'<span class="read">([^<]+)</span>', s).group(1)
        slug = os.path.splitext(os.path.basename(f))[0]
        jobs.append((f"og-{slug}.png", build_post(title, tag, date, read)))

    for name, html in jobs:
        hp = os.path.join(TMP, name.replace(".png", ".html"))
        open(hp, "w").write(html)
        dest = os.path.join(OUT, "img", name)
        subprocess.run([
            CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
            "--force-device-scale-factor=1", "--window-size=1200,630",
            "--virtual-time-budget=3000", f"--screenshot={dest}", f"file://{hp}",
        ], capture_output=True)
        print(f"{name:52} {os.path.getsize(dest)//1024:4d} KB")


if __name__ == "__main__":
    main()
