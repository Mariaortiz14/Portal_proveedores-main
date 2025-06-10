
const pdfjsLib = window['pdfjs-dist/build/pdf'];
  // Configurar la ubicación del script del trabajador
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@2.10.377/build/pdf.worker.min.js';

  // Variables globales
  var pdfDoc = null;
  var pageNum = 1;
  var pageRendering = false;
  var pageNumPending = null;

  // Función para mostrar una página específica
  function mostrarPagina(num, escala) {
    pageRendering = true;
    pdfDoc.getPage(num).then(function (page) {
      var viewport = page.getViewport({ scale: escala });

      pdfCanvas.width = viewport.width;
      pdfCanvas.height = viewport.height;

      visorPDF.style.height = pdfCanvas.height + 'px';

      //Renderizar la página que se vea con mejor calidad
      var renderContext = {
        canvasContext: pdfCanvas.getContext("2d", { alpha: false }),
        viewport: viewport,
      };
      //Renderizar la página 
      page.render(renderContext).promise.then(function () {
        pageRendering = false;
        if (pageNumPending !== null) {
          // Hay una página pendiente para renderizar
          mostrarPagina(pageNumPending, escala);
          pageNumPending = null;
        }
      });
    });

    // Actualizar número de página actual
    pageNum = num;
  }

  // Función para cambiar de página
  window.cambiarPagina = function (delta) {
    if (pageNum == 1 && delta == -1) {
      return;
    }
    if (pageNum == pdfDoc.numPages && delta == 1) {
      return;
    }
    mostrarPagina(pageNum + delta, escalaActual);
  }

  // Variables globales
  var pdfDoc = null;
  var pageNum = 1;
  var pageRendering = false;
  var pageNumPending = null;
  var escalaActual = 1.6;
  var zoomInButton = document.getElementById("zoomInButton");
  var zoomOutButton = document.getElementById("zoomOutButton");

  // Función para aumentar el zoom
  zoomInButton.addEventListener("click", function () {
    if (escalaActual >= 2.0) {
      return;
    }
    escalaActual += 0.1;
    mostrarPagina(pageNum, escalaActual);
  });

  // Función para disminuir el zoom
  zoomOutButton.addEventListener("click", function () {
    if (escalaActual <= 0.5) {
      return;
    }
    escalaActual -= 0.1;
    mostrarPagina(pageNum, escalaActual);
  });

  // Define la función mostrarPDF en el ámbito global
  function mostrarPDF(urlPDF) {
    var visorPDF = document.getElementById("visorPDF");
    var pdfCanvas = document.getElementById("pdfCanvas");
    var pdfLink = document.getElementById("pdfLink");

    // Actualizar el enlace para que apunte al PDF
    pdfLink.href = urlPDF;

    pdfjsLib.getDocument(urlPDF).promise.then(function (pdf) {
      pdfDoc = pdf;
      // Inicializar la primera página
      mostrarPagina(pageNum, escalaActual);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    // Move the cargarPDF function inside the DOMContentLoaded event listener




    window.cargarPDF = function (urlPDF) {
      pageNum = 1;
      escalaActual = 1.4;

      var pdfCanvas = document.getElementById("pdfCanvas");
      pdfCanvas.width = 0;
      pdfCanvas.height = 0;
      mostrarPDF(urlPDF);
    }
    const linkColor3 = document.querySelectorAll('.list_items')

    linkColor3.forEach(l => {
      // Verifica si el href del enlace coincide con la URL actual
      if (l.href === window.location.href) {
        // Si coincide, agrega la clase 'active'
        l.classList.add('active')
      } else {
        // Si no coincide, remueve la clase 'active'
        l.classList.remove('active')
      }
    })

    function colorLink3() {
      linkColor3.forEach(l => l.classList.remove('active'))
      this.classList.add('active')
    }

    linkColor3.forEach(l => l.addEventListener('click', colorLink3))

  });

  var navItems = document.querySelectorAll('.nav-link');

  navItems.forEach(function(item) {
      item.addEventListener('click', function() {
          localStorage.setItem('selectedNavItem', this.id);
      });
  });

  window.onload = function() {
    var selectedNavItem = localStorage.getItem('selectedNavItem');
    if (selectedNavItem) {
        // Buscar el elemento de navegación activo y desactivarlo
        var activeItem = document.querySelector('.nav-link.active');
        if (activeItem) {
            activeItem.classList.remove('active');
            var activeTab = document.querySelector(activeItem.dataset.bsTarget);
            activeTab.classList.remove('active', 'show');
        }

        // Activar el nuevo elemento de navegación
        var itemToSelect = document.querySelector(`.nav-link[id="${selectedNavItem}"]`);
        if (itemToSelect) {
            itemToSelect.classList.add('active');
            var tab = document.querySelector(itemToSelect.dataset.bsTarget);
            tab.classList.add('active', 'show');
        }
    }
};