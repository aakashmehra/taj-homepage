// TAJ Restaurant Website - Main JavaScript
// Modern interactive functionality for all pages

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Initialize smooth scrolling
    initializeSmoothScrolling();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize interactive elements
    initializeInteractiveElements();
    
    // Initialize page-specific functionality
    initializePageSpecific();
    
    console.log('TAJ Restaurant Website initialized successfully');
}

// Smooth scrolling functionality
function initializeSmoothScrolling() {
    // Add smooth scrolling to all internal links
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize animations and scroll effects
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all sections and cards
    const animatedElements = document.querySelectorAll('.menu-card, .location-card, .contact-method, .menu-section, .locations-section, .contact-section');
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    // Add parallax effect to hero background
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroBackground.style.transform = `translateY(${rate}px)`;
        });
    }
}

// Initialize interactive elements
function initializeInteractiveElements() {
    // Enhanced button hover effects
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Card hover effects
    const cards = document.querySelectorAll('.menu-card, .location-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Form enhancements
    const formInputs = document.querySelectorAll('.form-input, .form-textarea');
    
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });
}

// Page-specific functionality
function initializePageSpecific() {
    // Check current page and initialize specific features
    const currentPage = getCurrentPageType();
    
    switch(currentPage) {
        case 'home':
            initializeHomePage();
            break;
        case 'restaurant':
            initializeRestaurantPage();
            break;
        case 'menu':
            initializeMenuPage();
            break;
        case 'gallery':
            initializeGalleryPage();
            break;
        case 'contact':
            initializeContactPage();
            break;
        case 'about':
            initializeAboutPage();
            break;
    }
}

// Determine current page type
function getCurrentPageType() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index.html') return 'home';
    if (path.includes('/taj-') && path.includes('/menu')) return 'menu';
    if (path.includes('/taj-') && path.includes('/gallery')) return 'gallery';
    if (path.includes('/taj-')) return 'restaurant';
    if (path.includes('/contact')) return 'contact';
    if (path.includes('/about')) return 'about';
    
    return 'other';
}

// Home page specific initialization
function initializeHomePage() {
    // Hero section animations
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroDescription = document.querySelector('.hero-description');
    const heroButtons = document.querySelector('.hero-buttons');
    
    if (heroTitle) {
        setTimeout(() => heroTitle.classList.add('animate-slide-up'), 300);
        setTimeout(() => heroSubtitle.classList.add('animate-slide-up'), 600);
        setTimeout(() => heroDescription.classList.add('animate-slide-up'), 900);
        setTimeout(() => heroButtons.classList.add('animate-slide-up'), 1200);
    }
    
    // Scroll indicator animation
    const scrollIndicator = document.querySelector('.hero-scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', () => {
            scrollToSection('locations-section');
        });
    }
}

// Restaurant page specific initialization
function initializeRestaurantPage() {
    // Initialize restaurant-specific features
    const menuCards = document.querySelectorAll('.menu-card');
    
    menuCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('animate-fade-in');
        }, index * 200);
    });
    
    // Initialize photo carousel if present
    initializePhotoCarousel();
}

// Menu page specific initialization
function initializeMenuPage() {
    // Initialize menu-specific features
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuItems.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('animate-fade-in');
        }, index * 100);
    });
}

// Gallery page specific initialization
function initializeGalleryPage() {
    // Initialize gallery-specific features
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach((item, index) => {
        setTimeout(() => {
            item.classList.add('animate-fade-in');
        }, index * 50);
    });
}

// Contact page specific initialization
function initializeContactPage() {
    // Initialize contact form enhancements
    const contactForm = document.querySelector('.contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            // Add loading state to submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitBtn.disabled = true;
        });
    }
}

// About page specific initialization
function initializeAboutPage() {
    // Initialize about page animations
    const valueCards = document.querySelectorAll('.value-card');
    
    valueCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('animate-fade-in');
        }, index * 300);
    });
}

// Photo carousel functionality
function initializePhotoCarousel() {
    const carousel = document.querySelector('.carousel-container');
    if (!carousel) return;
    
    let currentSlide = 0;
    const slides = [];
    const carouselTrack = document.getElementById('carousel-track');
    
    // Load carousel images via API
    const location = getLocationFromUrl();
    if (location) {
        loadCarouselImages(location);
    }
}

// Load carousel images from API
async function loadCarouselImages(location) {
    try {
        const response = await fetch(`/api/gallery-images/${location}`);
        const images = await response.json();
        
        if (images && images.length > 0) {
            createCarouselSlides(images);
            startCarouselAutoplay();
        }
    } catch (error) {
        console.error('Failed to load carousel images:', error);
    }
}

// Create carousel slides
function createCarouselSlides(images) {
    const carouselTrack = document.getElementById('carousel-track');
    if (!carouselTrack) return;
    
    // Take first 5 images for carousel
    const carouselImages = images.slice(0, 5);
    
    carouselImages.forEach((image, index) => {
        const slide = document.createElement('div');
        slide.className = 'carousel-slide';
        slide.innerHTML = `
            <img src="${image.url}" alt="${image.alt}" loading="lazy">
            <div class="carousel-slide-overlay">
                <h3>${image.alt}</h3>
            </div>
        `;
        carouselTrack.appendChild(slide);
    });
    
    // Initialize carousel navigation
    initializeCarouselNavigation(carouselImages.length);
}

// Initialize carousel navigation
function initializeCarouselNavigation(totalSlides) {
    let currentSlide = 0;
    const carouselTrack = document.getElementById('carousel-track');
    
    // Previous button
    const prevBtn = document.querySelector('.carousel-prev');
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
            updateCarousel(currentSlide, carouselTrack);
        });
    }
    
    // Next button
    const nextBtn = document.querySelector('.carousel-next');
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentSlide = (currentSlide + 1) % totalSlides;
            updateCarousel(currentSlide, carouselTrack);
        });
    }
    
    // Auto-advance carousel
    setInterval(() => {
        currentSlide = (currentSlide + 1) % totalSlides;
        updateCarousel(currentSlide, carouselTrack);
    }, 5000);
}

// Update carousel position
function updateCarousel(slideIndex, track) {
    const slideWidth = 100;
    track.style.transform = `translateX(-${slideIndex * slideWidth}%)`;
}

// Start carousel autoplay
function startCarouselAutoplay() {
    // Autoplay is handled in initializeCarouselNavigation
}

// Get location from current URL
function getLocationFromUrl() {
    const path = window.location.pathname;
    const match = path.match(/\/taj-(\w+)/);
    return match ? match[1] : null;
}

// Utility functions
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Navigation helper functions
function navigateToHome() {
    window.location.href = '/';
}

function navigateToRestaurant(location) {
    window.location.href = `/taj-${location}`;
}

function navigateToMenu(location) {
    window.location.href = `/taj-${location}/menu`;
}

function navigateToGallery(location) {
    window.location.href = `/taj-${location}/gallery`;
}

function navigateToContact() {
    window.location.href = '/contact';
}

function navigateToAbout() {
    window.location.href = '/about';
}

// Animation helper functions
function addFadeInAnimation() {
    const style = document.createElement('style');
    style.textContent = `
        .animate-fade-in {
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .animate-slide-up {
            opacity: 0;
            transform: translateY(30px);
            animation: slideUp 0.8s ease-out forwards;
        }
        
        @keyframes fadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize animations CSS
addFadeInAnimation();

// Export functions for global use
window.TAJ = {
    scrollToSection,
    navigateToHome,
    navigateToRestaurant,
    navigateToMenu,
    navigateToGallery,
    navigateToContact,
    navigateToAbout
};
