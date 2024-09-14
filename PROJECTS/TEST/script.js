let canvas, ctx, columns, drops;

function createMatrixBackground() {
    console.log("Creating Matrix background");
    canvas = document.createElement('canvas');
    ctx = canvas.getContext('2d');
    const matrixBg = document.getElementById('matrix-bg');
    if (!matrixBg) {
        console.error("Element with id 'matrix-bg' not found");
        return;
    }
    matrixBg.appendChild(canvas);

    resizeCanvas();

    columns = Math.floor(canvas.width / 20);
    drops = new Array(columns).fill(1);

    animate();
}

function resizeCanvas() {
    console.log("Resizing canvas");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    columns = Math.floor(canvas.width / 20);
    drops = new Array(columns).fill(1);
}

function animate() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#00ffff';
    ctx.font = '15px monospace';

    const profileContainer = document.getElementById('profile-image-container');
    const containerRect = profileContainer.getBoundingClientRect();

    for (let i = 0; i < drops.length; i++) {
        const x = i * 20;
        const y = drops[i] * 20;

        if (x > containerRect.left && x < containerRect.right && y > containerRect.top && y < containerRect.bottom) {
            drops[i]++;
            continue;
        }

        const text = String.fromCharCode(Math.floor(Math.random() * 128));
        ctx.fillText(text, x, y);

        if (y > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    }

    requestAnimationFrame(animate);
}

function initCarousel() {
    const carousel = document.querySelector('.carousel');
    const container = document.querySelector('.carousel-container');
    let isHovering = false;
    let mouseX = 0;
    let scrollSpeed = 0;

    carousel.addEventListener('mouseenter', () => {
        isHovering = true;
    });

    carousel.addEventListener('mouseleave', () => {
        isHovering = false;
        scrollSpeed = 0;
    });

    carousel.addEventListener('mousemove', (e) => {
        if (!isHovering) return;
        
        const rect = carousel.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        mouseX = e.clientX - centerX;
        
        scrollSpeed = mouseX / (rect.width / 2) * 15;
    });

    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('click', (e) => {
            e.preventDefault();
            card.classList.add('clicked');
            
            setTimeout(() => {
                card.classList.remove('clicked');
                
                const repoUrl = card.dataset.repo;
                if (repoUrl) {
                    window.open(repoUrl, '_blank');
                }
            }, 500);
        });
    });

    function autoScroll() {
        if (isHovering) {
            carousel.scrollLeft += scrollSpeed;
        }
        requestAnimationFrame(autoScroll);
    }

    autoScroll();
}

function initSmoothScroll() {
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                // Remove glow from all sections
                document.querySelectorAll('section').forEach(section => {
                    section.classList.remove('glow');
                });

                // Add glow to target section
                targetSection.classList.add('glow');

                // Scroll to the target section
                const targetPosition = targetSection.getBoundingClientRect().top + window.pageYOffset;
                const offsetPosition = targetPosition - (window.innerHeight / 2) + (targetSection.offsetHeight / 2);

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                // Fade out glow effect
                setTimeout(() => {
                    targetSection.style.animation = 'smoothGlow 2s ease-in-out infinite';
                    targetSection.style.animationIterationCount = '1';
                }, 2000);

                // Remove glow class after animation ends
                setTimeout(() => {
                    targetSection.classList.remove('glow');
                    targetSection.style.animation = '';
                }, 4000);
            }
        });
    });
}

function init() {
    console.log("Initializing");
    createMatrixBackground();
    initCarousel();
    initSmoothScroll();
}

window.addEventListener('load', init);
window.addEventListener('resize', resizeCanvas);

if (document.readyState === 'complete') {
    console.log("Document already loaded, initializing immediately");
    init();
}

console.log("Script is running");