// Main JavaScript file for CompetitorAI
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();

    // Form handling
    initializeFormHandling();

    // UI enhancements
    initializeUIEnhancements();

    // Analytics and tracking
    initializeAnalytics();
});

function initializeApp() {
    console.log('CompetitorAI application initialized');

    // Add loading states to buttons
    addLoadingStates();

    // Initialize tooltips
    initializeTooltips();

    // Add smooth scrolling
    addSmoothScrolling();
}

function initializeFormHandling() {
    const analysisForm = document.getElementById('analysisForm');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (analysisForm && analyzeBtn) {
        analysisForm.addEventListener('submit', function(e) {
            // Validate form before submission
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }

            // Show loading state
            showLoadingState(analyzeBtn);

            // Store form data in localStorage for recovery
            storeFormData(this);
        });

        // Add real-time validation
        addRealTimeValidation(analysisForm);

        // Auto-save form data
        addAutoSave(analysisForm);
    }
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else if (field.type === 'url' && !isValidURL(field.value)) {
            showFieldError(field, 'Please enter a valid URL');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });

    return isValid;
}

function isValidURL(string) {
    try {
        // Add protocol if missing
        if (!string.match(/^https?:\/\//)) {
            string = 'https://' + string;
        }
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function showFieldError(field, message) {
    clearFieldError(field);

    field.classList.add('error');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function addRealTimeValidation(form) {
    const inputs = form.querySelectorAll('input');

    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required')) {
                if (!this.value.trim()) {
                    showFieldError(this, 'This field is required');
                } else if (this.type === 'url' && !isValidURL(this.value)) {
                    showFieldError(this, 'Please enter a valid URL');
                } else {
                    clearFieldError(this);
                }
            }
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                clearFieldError(this);
            }
        });
    });
}

function showLoadingState(button) {
    const btnText = button.querySelector('.btn-text');
    const spinner = button.querySelector('.loading-spinner');

    if (btnText && spinner) {
        button.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline-block';
    }
}

function storeFormData(form) {
    const formData = new FormData(form);
    const data = {};

    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }

    localStorage.setItem('competitorAnalysisFormData', JSON.stringify(data));
}

function addAutoSave(form) {
    const inputs = form.querySelectorAll('input, textarea, select');

    inputs.forEach(input => {
        input.addEventListener('input', debounce(() => {
            storeFormData(form);
        }, 1000));
    });

    // Restore form data on page load
    restoreFormData(form);
}

function restoreFormData(form) {
    const savedData = localStorage.getItem('competitorAnalysisFormData');

    if (savedData) {
        try {
            const data = JSON.parse(savedData);

            Object.entries(data).forEach(([key, value]) => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = value;
                }
            });
        } catch (e) {
            console.error('Error restoring form data:', e);
        }
    }
}

function initializeUIEnhancements() {
    // Add fade-in animations to cards
    addFadeInAnimations();

    // Initialize progress indicators
    initializeProgressIndicators();

    // Add copy-to-clipboard functionality
    addCopyToClipboard();

    // Initialize modal dialogs
    initializeModals();
}

function addFadeInAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    document.querySelectorAll('.result-section, .feature-card, .analysis-card').forEach(el => {
        observer.observe(el);
    });
}

function addCopyToClipboard() {
    const copyButtons = document.querySelectorAll('[data-copy]');

    copyButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const textToCopy = button.getAttribute('data-copy');

            try {
                await navigator.clipboard.writeText(textToCopy);
                showToast('Copied to clipboard!', 'success');

                // Visual feedback
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                button.classList.add('success');

                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.classList.remove('success');
                }, 2000);

            } catch (err) {
                showToast('Failed to copy text', 'error');
            }
        });
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));

            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function initializeProgressIndicators() {
    // Add progress bar for long-running operations
    const progressBar = document.createElement('div');
    progressBar.id = 'progressBar';
    progressBar.className = 'progress-bar';
    progressBar.innerHTML = '<div class="progress-fill"></div>';

    document.body.appendChild(progressBar);
}

function showProgress(percentage) {
    const progressBar = document.getElementById('progressBar');
    const progressFill = progressBar.querySelector('.progress-fill');

    progressBar.style.display = 'block';
    progressFill.style.width = `${percentage}%`;

    if (percentage >= 100) {
        setTimeout(() => {
            progressBar.style.display = 'none';
        }, 1000);
    }
}

function initializeAnalytics() {
    // Track user interactions
    trackFormSubmissions();
    trackButtonClicks();
    trackPageViews();
}

function trackFormSubmissions() {
    document.addEventListener('submit', function(e) {
        if (e.target.id === 'analysisForm') {
            console.log('Form submitted:', {
                timestamp: new Date().toISOString(),
                formId: e.target.id,
                userAgent: navigator.userAgent
            });
        }
    });
}

function trackButtonClicks() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn') || e.target.closest('.btn')) {
            const button = e.target.matches('.btn') ? e.target : e.target.closest('.btn');
            console.log('Button clicked:', {
                text: button.textContent.trim(),
                class: button.className,
                timestamp: new Date().toISOString()
            });
        }
    });
}

function trackPageViews() {
    console.log('Page view:', {
        url: window.location.href,
        title: document.title,
        timestamp: new Date().toISOString(),
        referrer: document.referrer
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// API helper functions
async function makeAPIRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Export functions for use in other scripts
window.CompetitorAI = {
    validateForm,
    showToast,
    showProgress,
    makeAPIRequest,
    debounce,
    throttle
};