document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // Mobile Navigation
    // ==========================================

    const menuButton = document.querySelector(".menu-toggle");
    const navigation = document.querySelector(".main-nav");

    if (menuButton && navigation) {
        menuButton.addEventListener("click", function () {
            navigation.classList.toggle("active");
            menuButton.classList.toggle("active");
        });
    }


    // ==========================================
    // Auto-hide Flash Messages
    // ==========================================

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.classList.add("flash-hide");

            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);
    });


    // ==========================================
    // Smooth Scroll
    // ==========================================

    const scrollLinks = document.querySelectorAll(
        'a[href^="#"]'
    );

    scrollLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {

            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (target) {
                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });


    // ==========================================
    // Reveal Elements on Scroll
    // ==========================================

    const revealElements = document.querySelectorAll(
        ".reveal, .fade-up"
    );

    if ("IntersectionObserver" in window) {

        const observer = new IntersectionObserver(
            function (entries, observerInstance) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {
                        entry.target.classList.add("visible");
                        observerInstance.unobserve(entry.target);
                    }

                });

            },
            {
                threshold: 0.12
            }
        );

        revealElements.forEach(function (element) {
            observer.observe(element);
        });

    } else {

        revealElements.forEach(function (element) {
            element.classList.add("visible");
        });

    }


    // ==========================================
    // Form Loading State
    // ==========================================

    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (!submitButton) {
                return;
            }

            if (submitButton.dataset.loading === "true") {
                return;
            }

            submitButton.dataset.loading = "true";

            if (submitButton.tagName === "BUTTON") {
                submitButton.textContent = "Please wait...";
            }

            submitButton.disabled = true;

        });

    });


    // ==========================================
    // External Links
    // ==========================================

    const externalLinks = document.querySelectorAll(
        'a[target="_blank"]'
    );

    externalLinks.forEach(function (link) {

        link.setAttribute(
            "rel",
            "noopener noreferrer"
        );

    });


    // ==========================================
    // Current Year
    // ==========================================

    const yearElements = document.querySelectorAll(
        "[data-current-year]"
    );

    yearElements.forEach(function (element) {
        element.textContent = new Date().getFullYear();
    });


    // ==========================================
    // Safar Setu Initialization
    // ==========================================

    console.log("Safar Setu JavaScript initialized.");

});