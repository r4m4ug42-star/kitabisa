document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.querySelector("#id_konten");
    if (!textarea) return;

    // tombol preview
    const btn = document.createElement("button");
    btn.type = "button";
    btn.innerText = "Preview Markdown";
    btn.style.margin = "10px 0";

    textarea.parentNode.appendChild(btn);

    // area preview
    const preview = document.createElement("div");
    preview.style.border = "1px solid #ddd";
    preview.style.padding = "10px";
    preview.style.marginTop = "10px";
    preview.style.background = "#fafafa";

    textarea.parentNode.appendChild(preview);

    btn.addEventListener("click", function () {
        fetch("/preview-markdown/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                konten: textarea.value
            })
        })
        .then(res => res.json())
        .then(data => {
            preview.innerHTML = data.html;
        });
    });
});
