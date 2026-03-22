{% load static %}

<textarea id="markdown-editor" name="content_md">
{{ lesson.content_md|default:'' }}
</textarea>

<link rel="stylesheet"
 href="https://unpkg.com/easymde/dist/easymde.min.css">
<script src="https://unpkg.com/easymde/dist/easymde.min.js"></script>

<script>
new EasyMDE({
    element: document.getElementById("markdown-editor"),
    spellChecker: false,
});
</script>

document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.getElementById("markdown-editor");
    if (!textarea) return;

    const easyMDE = new EasyMDE({
        element: textarea,
        spellChecker: false,
        autofocus: true,
        minHeight: "300px",
        placeholder: "Tulis materi kursus (Markdown)...",
        status: ["lines", "words", "cursor"],

        toolbar: [
            "bold", "italic", "heading",
            "|",
            "quote", "code", "table",
            "|",
            {
                name: "info",
                action: function customInfo(editor) {
                    const cm = editor.codemirror;
                    cm.replaceSelection(
`!!! info
    Tulis info di sini
`
                    );
                },
                className: "fa fa-info-circle",
                title: "Info Box"
            },
            {
                name: "warning",
                action: function customWarning(editor) {
                    const cm = editor.codemirror;
                    cm.replaceSelection(
`!!! warning
    Tulis peringatan di sini
`
                    );
                },
                className: "fa fa-exclamation-triangle",
                title: "Warning Box"
            },
            "|",
            "preview", "side-by-side", "fullscreen"
        ],
    });

    window.easyMDE = easyMDE;
});
