document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Mouse & Scroll Parallax Effect
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let currentX = window.innerWidth / 2;
    let currentY = window.innerHeight / 2;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.pageX;
        mouseY = e.pageY;
    });
    
    function animateParallax() {
        if(window.innerWidth >= 968) {
            currentX += (mouseX - currentX) * 0.08;
            currentY += (mouseY - currentY) * 0.08;
            const layers = document.querySelectorAll('.parallax-layer');
            layers.forEach(layer => {
                let speed = parseFloat(layer.getAttribute('data-speed')) || 0;
                if(speed !== 0) {
                    speed = speed * 1.5;
                    const x = (window.innerWidth / 2 - currentX) * speed;
                    const y = (window.innerHeight / 2 - currentY) * speed;
                    const scrollY = window.scrollY;
                    const scrollParallax = scrollY * (speed * -3);
                    layer.style.transform = `translateX(${x}px) translateY(${y + scrollParallax}px)`;
                }
            });
        }
        requestAnimationFrame(animateParallax);
    }
    animateParallax();

    // 2. Interactive 3D Login Cards
    const cards = document.querySelectorAll('.tilt-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            // Map mouse over the card to subtle rotation
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            const rotateX = -(y / rect.height) * 30; // 30 deg max
            const rotateY = (x / rect.width) * 30;
            
            card.style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = `rotateY(0deg) rotateX(0deg)`;
        });
    });

    // 3. GSAP Scroll Animations
    if(typeof gsap !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        // Hero Init
        gsap.from(".hero-title", {opacity: 0, y: 50, duration: 1.2, ease: "power3.out"});
        gsap.from(".hero-subtitle", {opacity: 0, y: 30, duration: 1, delay: 0.3});
        gsap.from(".btn-glow", {opacity: 0, scale: 0.8, duration: 1, delay: 0.6, ease: "elastic.out(1, 0.5)"});
        gsap.from(".section-title", {
            scrollTrigger: { trigger: ".impact-section", start: "top 80%" },
            opacity: 0, y: 30, duration: 1
        });

        // Scroll reveals for cards
        gsap.utils.toArray('.gsap-card').forEach((card, i) => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: ".image-grid",
                    start: "top 80%"
                },
                opacity: 0,
                y: 100,
                duration: 1,
                ease: "power2.out",
                delay: i * 0.2
            });
        });

        // Reveal login wrapper
        gsap.from(".login-section", {
            scrollTrigger: {
                trigger: ".logins-wrapper",
                start: "top 75%"
            },
            opacity: 0,
            scale: 0.9,
            rotationX: 15,
            duration: 1,
            stagger: 0.2,
            ease: "back.out(1.5)"
        });
    }
});
