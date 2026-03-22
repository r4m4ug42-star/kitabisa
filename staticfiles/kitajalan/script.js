function getMateri(pk) {
  fetch(`/get_materi/${pk}/`)
    .then(response => response.json())
    .then(data => {
      console.log('Data:', data); // tambahkan ini untuk memastikan data sudah benar
      const materiKursus = document.getElementById('materi-kursus');
      materiKursus.innerHTML = '';
      data.forEach(materi => {
        console.log('Materi:', materi); // tambahkan ini untuk memastikan data materi
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `${materi.konten.replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase()}.html`;
        a.textContent = materi.konten;
        li.appendChild(a);
        const p = document.createElement('p');
        p.textContent = materi.konten;
        materiKursus.appendChild(li);
        materiKursus.appendChild(p);
      });
    })
    .catch(error => console.error(error));
}