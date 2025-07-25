// initialization
const RESPONSIVE_WIDTH = 1024;

let headerWhiteBg = false;
let isHeaderCollapsed = window.innerWidth < RESPONSIVE_WIDTH;
const collapseBtn = document.getElementById("collapse-btn");
const collapseHeaderItems = document.getElementById("collapsed-header-items");

function onHeaderClickOutside(e) {
    // Prevent closing if clicking the collapse button or inside the menu
    if (!collapseHeaderItems.contains(e.target) && !collapseBtn.contains(e.target)) {
        toggleHeader();
    }
}

function toggleHeader() {
    if (isHeaderCollapsed) {
        collapseHeaderItems.classList.add("opacity-100");
        collapseHeaderItems.style.width = "60vw";
        collapseBtn.classList.remove("bi-list");
        collapseBtn.classList.add("bi-x", "max-lg:tw-fixed");
        isHeaderCollapsed = false;

        // Use requestAnimationFrame for smoother event handling
        requestAnimationFrame(() => {
            window.addEventListener("click", onHeaderClickOutside, { once: true });
        });
    } else {
        collapseHeaderItems.classList.remove("opacity-100");
        collapseHeaderItems.style.width = "0vw";
        collapseBtn.classList.remove("bi-x", "max-lg:tw-fixed");
        collapseBtn.classList.add("bi-list");
        isHeaderCollapsed = true;
        window.removeEventListener("click", onHeaderClickOutside);
    }
}

function responsive() {
    if (window.innerWidth > RESPONSIVE_WIDTH) {
        collapseHeaderItems.style.width = "";
    } else {
        isHeaderCollapsed = true;
    }
}

window.addEventListener("resize", responsive);

/**
 * Animations
 */
gsap.registerPlugin(ScrollTrigger);

gsap.to(".reveal-up", {
    opacity: 0,
    y: "100%",
});

gsap.to("#dashboard", {
    boxShadow: "0px 15px 25px -5px #7e22ceaa",
    duration: 0.3,
    scrollTrigger: {
        trigger: "#hero-section",
        start: "60% 60%",
        end: "80% 80%",
        // markers: true
    }
});

// straightens the slanting image
gsap.to("#dashboard", {
    scale: 1,
    translateY: 0,
    rotateX: "0deg",
    scrollTrigger: {
        trigger: "#hero-section",
        start: window.innerWidth > RESPONSIVE_WIDTH ? "top 95%" : "top 70%",
        end: "bottom bottom",
        scrub: 1,
        // markers: true,
    }
});

const faqAccordion = document.querySelectorAll('.faq-accordion');

faqAccordion.forEach(function (btn) {
    btn.addEventListener('click', function () {
        const content = this.nextElementSibling;
        const icon = this.querySelector('i');

        // Toggle active class for styling
        this.classList.toggle('active');

        // Toggle icon between plus and dash
        if (this.classList.contains('active')) {
            icon.classList.remove('bi-plus');
            icon.classList.add('bi-dash');
            content.style.maxHeight = content.scrollHeight + 'px';
            content.style.padding = '20px 18px';
        } else {
            icon.classList.remove('bi-dash');
            icon.classList.add('bi-plus');
            content.style.maxHeight = '0px';
            content.style.padding = '0px 18px';
        }
    });
});

// ------------- reveal section animations ---------------
const sections = gsap.utils.toArray("section");

sections.forEach((sec) => {
    const revealUptimeline = gsap.timeline({
        paused: true,
        scrollTrigger: {
            trigger: sec,
            start: "10% 80%", // top of trigger hits the top of viewport
            end: "20% 90%",
            // markers: true,
            // scrub: 1,
        }
    });

    revealUptimeline.to(sec.querySelectorAll(".reveal-up"), {
        opacity: 1,
        duration: 0.8,
        y: "0%",
        stagger: 0.2,
    });
});