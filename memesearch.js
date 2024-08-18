/*  memesearch.js
    Alternately shows or hides images on a page as search bar updates.
    Copyright (C) 2024 Henry Kroll III, www.thenerdshow.com

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/
const delayTime = 10; // milliseconds
let figures = document.querySelectorAll('figure');

function init() {
    let search = document.getElementById('search');
    search.addEventListener('keyup', filterFigures, true);
    search.addEventListener('click', (e) => {
        e.target.select();
        filterFigures(e);
    }, true);
}

function filterFigures(event) {
    if (event.key == "Escape") event.target.value = '';
    let searchTerm = event.target.value.trim().toLowerCase();
    if (searchTerm.length == 0) searchTerm = ' ';
    figures.forEach(figure => {
        if (!figure.querySelector('figcaption')) {
            console.log(figure.querySelector('img').src);
            figure.style.display = 'inline-block';
        } else
        if (figure.querySelector('figcaption').innerText.toLowerCase()
            .includes(searchTerm))
            figure.style.display = 'inline-block';
        else figure.style.display = 'none';
    });
}
init();
