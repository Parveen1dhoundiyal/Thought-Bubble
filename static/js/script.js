
const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav');

menuToggle.addEventListener('click', function() {
    nav.classList.toggle('showing');
});

// Ensure submenus are also visible when showing the main nav
const subMenus = document.querySelectorAll('header ul li ul');
nav.addEventListener('click', function() {
    subMenus.forEach(menu => {
        menu.style.display = 'block';
    });
});

$(document).ready(function(){
    $('.post-slider-container').slick({
        dots: true,
        infinite: true,
        speed: 300,
        slidesToShow: 3, // Default number of slides to show
        adaptiveHeight: true,
        autoplay: true,
        autoplaySpeed: 2000,
        prevArrow: $('.slick-prev'),
        nextArrow: $('.slick-next'),
        responsive: [
            {
                breakpoint: 1024, // Screen width under 1024px
                settings: {
                    slidesToShow: 2, // Show 2 slides instead of 3
                    slidesToScroll: 1,
                    infinite: true,
                    dots: true
                }
            },
            {
                breakpoint: 768, // Screen width under 768px
                settings: {
                    slidesToShow: 1, // Show 1 slide instead of 3
                    slidesToScroll: 1,
                    infinite: true,
                    dots: true
                }
            },
            {
                breakpoint: 480, // Screen width under 480px
                settings: {
                    slidesToShow: 1, // Show 1 slide instead of 3
                    slidesToScroll: 1,
                    dots: true
                }
            }
        ]
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebarClose = document.querySelector('.sidebar-close');
    const sidebar = document.querySelector('.sidebar');
    const toggleIcon = sidebarToggle.querySelector('i');

    function openSidebar() {
        sidebar.classList.add('show');
        toggleIcon.classList.remove('fa-chevron-right');
        toggleIcon.classList.add('fa-chevron-left');
    }

    function closeSidebar() {
        sidebar.classList.remove('show');
        toggleIcon.classList.remove('fa-chevron-left');
        toggleIcon.classList.add('fa-chevron-right');
    }

    sidebarToggle.addEventListener('click', openSidebar);
    sidebarClose.addEventListener('click', closeSidebar);

    // Close sidebar when clicking outside of it
    document.addEventListener('click', function(event) {
        if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target) && sidebar.classList.contains('show')) {
            closeSidebar();
        }
    });
});

