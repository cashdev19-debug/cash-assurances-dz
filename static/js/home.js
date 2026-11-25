(function () {
    'use strict';
    const slides = window.carouselSlides || [];
    if (slides.length === 0) return;
    const MAIN_COLOR = '#b61615';
    const INACTIVE_COLOR = '#d1d5db';
    const SLIDE_DURATION = 10000;
    const TRANSITION_DURATION = 800;
    const wrapper = document.getElementById('carousel');
    const slideCounter = document.getElementById('slideCounter');
    const slideTitle = document.getElementById('slideTitle');
    const slideSubtitle = document.getElementById('slideSubtitle');
    const slideDescription = document.getElementById('slideDescription');
    const slideButton = document.getElementById('slideButton');
    const slideImage = document.getElementById('slideImage');
    const collectionNum = document.getElementById('collectionNum');
    const navArrows = document.getElementById('navArrows');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const progressBar = document.getElementById('progressBar');
    let currentIndex = 0;
    let isTransitioning = false;
    let isPaused = false;
    let progress = 0;
    let slideInterval = null;
    let progressInterval = null;
    let touchStartX = 0;
    let touchEndX = 0;
    function getSlide(index) {
        return slides[index % slides.length];
    }
    function updateProgressFill(index, value) {
        if (!progressBar) return;
        const items = progressBar.querySelectorAll('.carousel-progress-item');
        items.forEach((item, i) => {
            const fill = item.querySelector('.carousel-progress-fill');
            if (!fill) return;
            if (i === index) {
                fill.style.width = value + '%';
            } else if (i < index) {
                fill.style.width = '100%';
            } else {
                fill.style.width = '0%';
            }
        });
    }
    function setActiveProgress(index) {
        if (!progressBar) return;
        const items = progressBar.querySelectorAll('.carousel-progress-item');
        items.forEach((item, i) => {
            item.classList.toggle('active', i === index);
            const fill = item.querySelector('.carousel-progress-fill');
            if (!fill) return;
            fill.style.backgroundColor = i === index ? MAIN_COLOR : INACTIVE_COLOR;
        });
    }
    function renderSlide(index, animate = true) {
        const slide = getSlide(index);
        const total = slides.length;
        if (slideCounter) {
            slideCounter.textContent =
                String(index + 1).padStart(2, '0') + ' / ' + String(total).padStart(2, '0');
        }
        if (slideTitle) slideTitle.textContent = slide.title;
        if (slideSubtitle) slideSubtitle.textContent = slide.subtitle;
        if (slideDescription) slideDescription.textContent = slide.description;
        if (slideButton) {
            slideButton.textContent = slide.button;
            if (slide.buttonUrl) {
                slideButton.href = slide.buttonUrl;
                slideButton.style.display = '';
            } else {
                slideButton.removeAttribute('href');
                slideButton.style.display = slide.button ? '' : 'none';
            }
        }
        if (slideImage) {
            slideImage.src = slide.imageUrl;
            slideImage.alt = slide.title;
        }
        setActiveProgress(index);
        const contentEls = [collectionNum, slideTitle, slideSubtitle, slideDescription, slideButton, navArrows].filter(Boolean);
        const imageEl = slideImage;
        if (animate) {
            contentEls.forEach((el) => {
                el.classList.remove('enter');
                el.classList.add('exit');
            });
            if (imageEl) {
                imageEl.classList.remove('enter');
                imageEl.classList.add('exit');
            }
            setTimeout(() => {
                contentEls.forEach((el) => {
                    el.classList.remove('exit');
                    el.classList.add('enter');
                });
                if (imageEl) {
                    imageEl.classList.remove('exit');
                    imageEl.classList.add('enter');
                }
            }, TRANSITION_DURATION / 2);
        } else {
            contentEls.forEach((el) => {
                el.classList.remove('exit');
                el.classList.add('enter');
            });
            if (imageEl) {
                imageEl.classList.remove('exit');
                imageEl.classList.add('enter');
            }
        }

        progress = 0;
        updateProgressFill(index, 0);
    }
    function goToSlide(index) {
        if (isTransitioning || index === currentIndex) return;
        const target = ((index % slides.length) + slides.length) % slides.length;
        if (target === currentIndex) return;
        isTransitioning = true;
        stopAutoAdvance();
        renderSlide(target, true);
        setTimeout(() => {
            currentIndex = target;
            isTransitioning = false;
            progress = 0;
            updateProgressFill(currentIndex, 0);
            startAutoAdvance();
        }, TRANSITION_DURATION + 100);
    }
    function goNext() {
        goToSlide(currentIndex + 1);
    }
    function goPrev() {
        goToSlide(currentIndex - 1);
    }
    function startAutoAdvance() {
        stopAutoAdvance();
        if (isPaused) return;
        progressInterval = setInterval(() => {
            if (isTransitioning || isPaused) return;
            progress = Math.min(progress + 100 / (SLIDE_DURATION / 50), 100);
            updateProgressFill(currentIndex, progress);
        }, 50);
        slideInterval = setInterval(() => {
            if (isTransitioning || isPaused) return;
            goNext();
        }, SLIDE_DURATION);
    }
    function stopAutoAdvance() {
        if (slideInterval) {
            clearInterval(slideInterval);
            slideInterval = null;
        }
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }
    function pauseAutoAdvance() {
        isPaused = true;
        stopAutoAdvance();
    }
    function resumeAutoAdvance() {
        isPaused = false;
        startAutoAdvance();
    }
    function buildProgressBar() {
        if (!progressBar) return;
        progressBar.innerHTML = '';
        slides.forEach((slide, index) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'carousel-progress-item';
            btn.setAttribute('aria-label', 'Go to slide ' + (index + 1));
            const track = document.createElement('div');
            track.className = 'carousel-progress-track';
            const fill = document.createElement('div');
            fill.className = 'carousel-progress-fill';
            fill.style.width = index < currentIndex ? '100%' : '0%';
            fill.style.backgroundColor = index === currentIndex ? MAIN_COLOR : INACTIVE_COLOR;
            track.appendChild(fill);
            btn.appendChild(track);

            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                goToSlide(index);
            });
            progressBar.appendChild(btn);
        });
        setActiveProgress(currentIndex);
    }

    function handleTouchStart(e) {
        touchStartX = e.touches[0].clientX;
        touchEndX = touchStartX; 
    }

    function handleTouchMove(e) {
        touchEndX = e.touches[0].clientX;
    }

    function handleTouchEnd() {
        const diff = touchStartX - touchEndX;
        if (Math.abs(diff) > 60) {
            if (diff > 0) goNext();
            else goPrev();
        }
    }

    function handleKeydown(e) {
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            goNext();
        }
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            goPrev();
        }
    }
    function init() {
        buildProgressBar();
        renderSlide(0, false);
        setTimeout(startAutoAdvance, 400);
        if (wrapper) {
            wrapper.addEventListener('touchstart', handleTouchStart, { passive: true });
            wrapper.addEventListener('touchmove', handleTouchMove, { passive: true });
            wrapper.addEventListener('touchend', handleTouchEnd, { passive: true });
        }
        document.addEventListener('keydown', handleKeydown);
        if (prevBtn) prevBtn.addEventListener('click', (e) => { e.stopPropagation(); goPrev(); });
        if (nextBtn) nextBtn.addEventListener('click', (e) => { e.stopPropagation(); goNext(); });

        window.addEventListener('beforeunload', () => {
            stopAutoAdvance();
            document.removeEventListener('keydown', handleKeydown);
        });
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) pauseAutoAdvance();
            else resumeAutoAdvance();
        });
    }
    init();
})();