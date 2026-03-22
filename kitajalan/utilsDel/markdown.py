import markdown
import bleach

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS | {
    "p", "pre", "code", "span",
    "h1", "h2", "h3", "h4",
    "blockquote", "div"
}

ALLOWED_ATTRS = {
    "*": ["class"],
}

def render_markdown(text):
    html = markdown.markdown(
        text,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "admonition"
        ],
    )

    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
    )