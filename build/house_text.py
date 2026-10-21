"""House rule 1 (house-rules.md): Jiu-Jitsu with both Js capital, applied to a finished page.

    from house_text import house_text
    html = house_text(html)          # the last step before a build script writes a page

Fixes what a person or a search engine reads: text between tags, the readable attributes (alt,
title, aria-label, placeholder, meta content, data-label) and the strings inside JSON-LD. Leaves
alone what a machine reads: URLs and slugs (href, src, srcset, og:url, JSON-LD urls), ids, classes,
form values, and the code inside <script> and <style>. Only the two Js change: "jiu-jitsu" becomes
"Jiu-Jitsu", "jiu jitsu" becomes "Jiu Jitsu", "JIU-JITSU" stays as it is.

Copy this file into a project's build folder and import it there; the skill's copy is the master.
"""
import re

# jiu + any hyphen, space or joiner + jitsu, not inside a longer word, URL or anchor
_SEP = r"(?:[\s ‐‑⁠-]|&nbsp;|&#x2011;|&#8209;)*"
_WORD = re.compile(r"(?<![A-Za-z0-9/_.#=&-])([jJ])([iI][uU])(" + _SEP + r")([jJ])([iI][tT][sS][uU])(?![A-Za-z0-9_])")

# attributes whose value is read by people or shown in search results
_READ = ("alt", "title", "aria-label", "aria-description", "placeholder", "data-label", "label")
_ATTR = re.compile(r"""(\s)([a-zA-Z_:][-a-zA-Z0-9_:.]*)(\s*=\s*)("[^"]*"|'[^']*')""")
_RAW = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.S | re.I)
_TOKENS = re.compile(r"(<!--.*?-->|<[^>]*>)", re.S)
_URLISH = re.compile(r"^\s*(https?:|mailto:|tel:|/|#|\.)", re.I)
_URL_KEYS = ("url", "@id", "image", "logo", "sameAs", "item", "contentUrl", "thumbnailUrl", "embedUrl", "hasMap")


def fix_words(text):
    """Capitalise both Js in every Jiu-Jitsu of a plain string."""
    return _WORD.sub(lambda m: "J" + m.group(2) + m.group(3) + "J" + m.group(5), text)


def _fix_tag(tag):
    low = tag[:12].lower()
    if tag.startswith("<!--") or low.startswith(("<!doctype", "</")):
        return tag
    is_meta = low.startswith("<meta")

    def one(m):
        name, val = m.group(2).lower(), m.group(4)
        inner = val[1:-1]
        if name in _READ or (is_meta and name == "content" and not _URLISH.match(inner)):
            return m.group(1) + m.group(2) + m.group(3) + val[0] + fix_words(inner) + val[-1]
        return m.group(0)
    return _ATTR.sub(one, tag)


def _fix_jsonld(block):
    """Strings in a JSON-LD script, except the values of URL keys."""
    head_end = block.index(">") + 1
    body, tail = block[head_end:-len("</script>")], block[-len("</script>"):]
    keys = "|".join(re.escape(k) for k in _URL_KEYS)
    # split into "key": "value" pairs we must keep and everything else we may fix
    keep = re.compile(r'("(?:' + keys + r')"\s*:\s*)("(?:[^"\\]|\\.)*"|\[[^\]]*\])')
    out, pos = [], 0
    for m in keep.finditer(body):
        out.append(fix_words(body[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(fix_words(body[pos:]))
    return block[:head_end] + "".join(out) + tail


def house_text(html):
    """Apply the house rules to a whole page (or fragment) of HTML."""
    out, pos = [], 0
    for m in _RAW.finditer(html):
        out.append(_fix_markup(html[pos:m.start()]))
        block = m.group(0)
        if m.group(1).lower() == "script" and re.match(r"<script\b[^>]*application/ld\+json", block, re.I):
            block = _fix_jsonld(block)
        else:
            block = _fix_tag(block[:block.index(">") + 1]) + block[block.index(">") + 1:]
        out.append(block)
        pos = m.end()
    out.append(_fix_markup(html[pos:]))
    return "".join(out)


def _fix_markup(chunk):
    parts = _TOKENS.split(chunk)
    return "".join(_fix_tag(p) if p.startswith("<") else fix_words(p) for p in parts)


if __name__ == "__main__":
    sample = ('<title>jiu-jitsu classes</title><meta name="description" content="Brazilian jiu-jitsu in town">'
              '<meta property="og:url" content="https://x.com/programs/jiu-jitsu/">'
              '<a href="/programs/jiu-jitsu/" class="jiu-jitsu" id="jiu-jitsu" title="jiu jitsu">MMA or jiu-jitsu?</a>'
              '<img src="/img/jiu-jitsu.jpg" alt="a jiu-jitsu class"><input type="hidden" name="p" value="jiu-jitsu">'
              '<p>JIU-JITSU, Jiu-jitsu, jiu&nbsp;jitsu, jiu-⁠jitsu, jiujitsucon, @longosjiujitsu</p>'
              '<script>var s = "jiu-jitsu";</script>'
              '<script type="application/ld+json">{"name": "jiu jitsu academy", "url": "https://x.com/jiu-jitsu", "sameAs": ["https://ig.com/jiu-jitsu"]}</script>')
    print(house_text(sample))
