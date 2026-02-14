/**
 * Main JavaScript for Alumni Donation System
 */

// Global Configuration
const CONFIG = {
    apiBaseUrl: '',
    razorpayKey: '',
    minDonationAmount: 100
};

// Utility Functions
const Utils = {
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(amount);
    },
    
    // Format date
    formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('en-IN', options);
    },
    
    // Validate email
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },
    
    // Show loading spinner
    showLoading(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        element.appendChild(spinner);
        return spinner;
    },
    
    // Hide loading spinner
    hideLoading(spinner) {
        if (spinner && spinner.parentNode) {
            spinner.parentNode.removeChild(spinner);
        }
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Copy to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    }
};

// Form Validation
class FormValidator {
    constructor(formElement) {
        this.form = formElement;
        this.errors = {};
    }
    
    validate(rules) {
        this.errors = {};
        
        for (const [field, fieldRules] of Object.entries(rules)) {
            const input = this.form.querySelector(`[name="${field}"]`);
            const value = input?.value?.trim();
            
            // Required validation
            if (fieldRules.required && !value) {
                this.errors[field] = `${fieldRules.label} is required`;
                continue;
            }
            
            // Email validation
            if (fieldRules.email && value && !Utils.isValidEmail(value)) {
                this.errors[field] = 'Please enter a valid email address';
                continue;
            }
            
            // Min value validation
            if (fieldRules.min && value && parseFloat(value) < fieldRules.min) {
                this.errors[field] = `${fieldRules.label} must be at least ${fieldRules.min}`;
                continue;
            }
            
            // Max value validation
            if (fieldRules.max && value && parseFloat(value) > fieldRules.max) {
                this.errors[field] = `${fieldRules.label} must not exceed ${fieldRules.max}`;
                continue;
            }
            
            // Pattern validation
            if (fieldRules.pattern && value && !fieldRules.pattern.test(value)) {
                this.errors[field] = fieldRules.message || `Invalid ${fieldRules.label}`;
            }
        }
        
        return Object.keys(this.errors).length === 0;
    }
    
    showErrors() {
        // Clear previous errors
        this.form.querySelectorAll('.error-message').forEach(el => el.remove());
        this.form.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
        
        // Display new errors
        for (const [field, message] of Object.entries(this.errors)) {
            const input = this.form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('error');
                
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = message;
                
                input.parentNode.appendChild(errorDiv);
            }
        }
    }
}

// API Service
const API = {
    async request(endpoint, options = {}) {
        const url = `${CONFIG.apiBaseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    createOrder(donationData) {
        return this.request('/api/create-order', {
            method: 'POST',
            body: JSON.stringify(donationData)
        });
    },
    
    verifyPayment(paymentData) {
        return this.request('/api/verify-payment', {
            method: 'POST',
            body: JSON.stringify(paymentData)
        });
    },
    
    sendBulkEmail(emailData) {
        return this.request('/admin/send-email', {
            method: 'POST',
            body: JSON.stringify(emailData)
        });
    }
};

// Donation Handler
class DonationHandler {
    constructor(formId, razorpayKey) {
        this.form = document.getElementById(formId);
        this.razorpayKey = razorpayKey;
        this.validator = new FormValidator(this.form);
        
        if (this.form) {
            this.init();
        }
    }
    
    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        // Validation rules
        const rules = {
            name: { required: true, label: 'Name' },
            email: { required: true, email: true, label: 'Email' },
            batch_year: { required: true, label: 'Batch Year' },
            amount: { 
                required: true, 
                min: CONFIG.minDonationAmount, 
                label: 'Amount' 
            }
        };
        
        if (!this.validator.validate(rules)) {
            this.validator.showErrors();
            return;
        }
        
        const formData = new FormData(this.form);
        const donationData = {
            name: formData.get('name'),
            email: formData.get('email'),
            batch_year: formData.get('batch_year'),
            amount: formData.get('amount'),
            message: formData.get('message') || ''
        };
        
        try {
            // Create Razorpay order
            const orderData = await API.createOrder(donationData);
            
            if (!orderData.success) {
                throw new Error(orderData.message);
            }
            
            // Open Razorpay payment
            this.openRazorpay(orderData, donationData);
            
        } catch (error) {
            Utils.showNotification(error.message, 'error');
        }
    }
    
    openRazorpay(orderData, donationData) {
        const options = {
            key: this.razorpayKey,
            amount: orderData.amount,
            currency: 'INR',
            name: 'Alumni Network',
            description: 'Donation',
            order_id: orderData.order_id,
            handler: (response) => this.handlePaymentSuccess(response, donationData),
            prefill: {
                name: donationData.name,
                email: donationData.email
            },
            theme: {
                color: '#667eea'
            }
        };
        
        const rzp = new Razorpay(options);
        
        rzp.on('payment.failed', (response) => {
            Utils.showNotification('Payment failed: ' + response.error.description, 'error');
        });
        
        rzp.open();
    }
    
    async handlePaymentSuccess(response, donationData) {
        try {
            const verifyData = await API.verifyPayment({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                ...donationData
            });
            
            if (verifyData.success) {
                Utils.showNotification(
                    'Thank you for your donation! Certificate sent to your email.',
                    'success'
                );
                this.form.reset();
                
                // Reload page after 2 seconds to update stats
                setTimeout(() => window.location.reload(), 2000);
            } else {
                throw new Error(verifyData.message);
            }
            
        } catch (error) {
            Utils.showNotification(
                'Payment verification failed. Please contact support.',
                'error'
            );
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Alumni Donation System initialized');
    
    // Initialize donation form if present
    const razorpayKey = document.querySelector('[data-razorpay-key]')?.dataset.razorpayKey;
    if (razorpayKey) {
        CONFIG.razorpayKey = razorpayKey;
        new DonationHandler('donationForm', razorpayKey);
    }
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Auto-dismiss alerts
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Export for use in other scripts
window.AlumniSystem = {
    Utils,
    API,
    FormValidator,
    DonationHandler
}; 