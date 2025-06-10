document.addEventListener("DOMContentLoaded", function(event) {
   
    const showNavbar = (toggleId, navId, bodyId, headerId) =>{
    const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId),
    bodypd = document.getElementById(bodyId),
    headerpd = document.getElementById(headerId)
    
    // Validate that all variables exist
    if(toggle && nav && bodypd && headerpd){
    toggle.addEventListener('click', ()=>{
    // show navbar
    nav.classList.toggle('show1')
    // change icon
    toggle.classList.toggle('bx-x')
    toggle.classList.toggle('ms-4')
    // add padding to body
    bodypd.classList.toggle('body-pd')
    // add padding to header
    headerpd.classList.toggle('body-pd')
    })
    }
    }
    
    showNavbar('header-toggle','nav-bar','body-pd','header')
    
    /*===== LINK ACTIVE =====*/
    const linkColor = document.querySelectorAll('.nav_link')

    linkColor.forEach(l => {
        // Verifica si el href del enlace coincide con la URL actual
        if (l.href === window.location.href) {
            // Si coincide, agrega la clase 'active'
            l.classList.add('active')
        } else {
            // Si no coincide, remueve la clase 'active'
            l.classList.remove('active')
        }
    })
    
    function colorLink() {
        linkColor.forEach(l => l.classList.remove('active'))
        this.classList.add('active')
    }
    
    linkColor.forEach(l => l.addEventListener('click', colorLink))

    const linkColor2 = document.querySelectorAll('.coll-nav')

    linkColor2.forEach(l => {
        // Verifica si el href del enlace coincide con la URL actual
        if (l.href === window.location.href) {
            // Si coincide, agrega la clase 'active'
            l.classList.add('active')
        } else {
            // Si no coincide, remueve la clase 'active'
            l.classList.remove('active')
        }
    })
    
    function colorLink2() {
        linkColor2.forEach(l => l.classList.remove('active'))
        this.classList.add('active')
    }
    
    linkColor2.forEach(l => l.addEventListener('click', colorLink2))
    
    
     // Your code to run since DOM is loaded and ready
});
