document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    // Initialize the modals
    const bookModal = new bootstrap.Modal(document.getElementById('bookModal'));
    const profileModal = new bootstrap.Modal(document.getElementById('profileModal'));
    const editProfileModal = new bootstrap.Modal(document.getElementById('editProfileModal'));
    const activeBookingModal = new bootstrap.Modal(document.getElementById('activeBookingModal'));
    console.log('Modal elements:', {
        bookModal: document.getElementById('bookModal'),
        profileModal: document.getElementById('profileModal'),
        editProfileModal: document.getElementById('editProfileModal'),
        activeBookingModal: document.getElementById('activeBookingModal')
    });
    
    // Booking Flow Validation Functions
    const BookingValidator = {
        async checkActiveBookings() {
            try {
                const response = await fetch('/api/check-active-booking');
                const data = await response.json();
                return data.hasActiveBooking;
            } catch (error) {
                console.error('Error checking active bookings:', error);
                return false;
            }
        },
        
        isProfileComplete() {
            const userAddress = document.querySelector('.lot-book-btn').dataset.userAddress;
            const userPincode = document.querySelector('.lot-book-btn').dataset.userPincode;
            return userAddress && userPincode;
        },
        
        async validateBookingEligibility() {
            const hasActiveBooking = await this.checkActiveBookings();
            if (hasActiveBooking) {
                showErrorMessage("Booking Failed: You already have an active booking. Please vacate or cancel it before booking a new spot.");
                return false;
            }
            
            if (!this.isProfileComplete()) {
                profileModal.show();
                return false;
            }
            
            return true;
        }
    };
    
    // Booking Modal Handler
    const BookingModalHandler = {
        updateModalContent(button) {
            const lotId = button.dataset.lotId;
            const lotName = button.dataset.lotName;
            const address = button.dataset.address;
            const pincode = button.dataset.pincode;
            const price = button.dataset.price;
            
            // Update modal content
            document.getElementById('modalLotId').value = lotId;
            document.getElementById('modalLotName').textContent = lotName;
            document.getElementById('modalPrice').textContent = `₹${price}/hr`;
        },
        
        resetForm() {
            const form = document.getElementById('bookingForm');
            form.reset();
        }
    };
    
    // Profile Update Handler
    const ProfileUpdateHandler = {
        async handleProfileUpdate(event) {
            event.preventDefault();
            const button = event.target;
            const form = document.getElementById('editProfileForm');
            const successAlert = document.getElementById('profileUpdateSuccess');
            const errorAlert = document.getElementById('profileUpdateError');
            const spinner = button.querySelector('.spinner-border');
            
            // Reset alerts and show loading state
            successAlert.classList.add('d-none');
            errorAlert.classList.add('d-none');
            button.disabled = true;
            spinner.classList.remove('d-none');
            
            try {
                const formData = new FormData(form);
                const response = await fetch('/user/edit_profile', {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Update user data in book buttons
                    document.querySelectorAll('.lot-book-btn').forEach(btn => {
                        btn.dataset.userAddress = formData.get('address');
                        btn.dataset.userPincode = formData.get('pincode');
                    });
                    
                    successAlert.classList.remove('d-none');
                    
                    if (BookingValidator.isProfileComplete()) {
                        setTimeout(() => {
                            editProfileModal.hide();
                            bookModal.show();
                        }, 1500);
                    }
                } else {
                    errorAlert.querySelector('span').textContent = data.message || 'Failed to update profile. Please try again.';
                    errorAlert.classList.remove('d-none');
                }
            } catch (error) {
                console.error('Error:', error);
                errorAlert.querySelector('span').textContent = 'An error occurred. Please try again.';
                errorAlert.classList.remove('d-none');
            } finally {
                button.disabled = false;
                spinner.classList.add('d-none');
            }
        }
    };
    
    // Function to show error message
    function showErrorMessage(message) {
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
        errorAlert.style.zIndex = '9999';
        errorAlert.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            <strong>Error!</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert the alert at the top of the body
        document.body.appendChild(errorAlert);
        
        // Remove the alert after 5 seconds
        setTimeout(() => {
            errorAlert.remove();
        }, 5000);
    }
    
    // Function to show warning modal
    function showWarningModal() {
        const warningModal = new bootstrap.Modal(document.getElementById('activeBookingWarningModal'));
        warningModal.show();
    }
    
    // Function to show success message
    function showSuccessMessage(message) {
        const successAlert = document.createElement('div');
        successAlert.className = 'alert alert-success alert-dismissible fade show';
        successAlert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>Success!</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert the alert at the top of the container
        const container = document.querySelector('.container-fluid');
        container.insertBefore(successAlert, container.firstChild);
        
        // Remove the alert after 5 seconds
        setTimeout(() => {
            successAlert.remove();
        }, 5000);
    }
    
    // Search, Sort, and Filter Functionality
    const ParkingLotsManager = {
        lots: [], // Will store all parking lots
        searchTimeout: null, // For debouncing search
        isInitialLoad: true, // Flag to track initial load

        initialize() {
            this.loadParkingLots();
            this.setupEventListeners();
        },

        async loadParkingLots() {
            try {
                const response = await fetch('/api/parking-lots');
                if (!response.ok) throw new Error('Failed to fetch parking lots');
                this.lots = await response.json();
                
                // Only render if it's not the initial load
                if (!this.isInitialLoad) {
                this.renderParkingLots(this.lots);
                }
                this.isInitialLoad = false;
            } catch (error) {
                console.error('Error loading parking lots:', error);
                this.showErrorMessage('Failed to load parking lots. Please refresh the page.');
            }
        },

        setupEventListeners() {
            // Search functionality with debouncing
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    clearTimeout(this.searchTimeout);
                    this.searchTimeout = setTimeout(() => {
                    this.filterLots();
                    }, 200); // 200ms debounce
                });
            }

            // Sort functionality
            const sortSelect = document.getElementById('sortSelect');
            if (sortSelect) {
                sortSelect.addEventListener('change', () => {
                    this.sortLots();
                });
            }
        },

        filterLots() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
            
            let filteredLots = this.lots.filter(lot => {
                // Check for exact pincode match first
                if (searchTerm && lot.pincode === searchTerm) {
                    return true;
                }
                
                // Then check for partial name match
                if (searchTerm && lot.name.toLowerCase().includes(searchTerm)) {
                    return true;
                }
                
                // If no search term, show all lots
                return !searchTerm;
            });

            this.sortLots(filteredLots);
        },

        sortLots(lots = null) {
            const sortValue = document.getElementById('sortSelect').value;
            const lotsToSort = lots || this.lots;

            let sortedLots = [...lotsToSort];
            switch (sortValue) {
                case 'price-asc':
                    sortedLots.sort((a, b) => a.price_per_hour - b.price_per_hour);
                    break;
                case 'price-desc':
                    sortedLots.sort((a, b) => b.price_per_hour - a.price_per_hour);
                    break;
                case 'spots':
                    sortedLots.sort((a, b) => b.available_spots - a.available_spots);
                    break;
                default:
                    // Default sort by proximity (if location data is available)
                    // For now, just maintain original order
                    break;
            }

            this.renderParkingLots(sortedLots);
        },

        renderParkingLots(lots) {
            const container = document.getElementById('parkingLotsContainer');
            if (!container) return;

            // Only update if there's a change in the results
            if (container.children.length !== lots.length || 
                document.getElementById('searchInput').value.trim() !== '' ||
                document.getElementById('sortSelect').value !== 'price-asc') {

            container.innerHTML = '';
            
            if (lots.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-search fa-3x mb-3 text-muted"></i>
                        <h4 class="text-muted">No parking lots found</h4>
                            <p class="text-muted">Try adjusting your search criteria</p>
                    </div>
                `;
                return;
            }

            lots.forEach(lot => {
                const card = this.createParkingLotCard(lot);
                container.appendChild(card);
            });

            // Reattach event listeners to the new cards
            this.reattachEventListeners();
            }
        },

        createParkingLotCard(lot) {
            const col = document.createElement('div');
            col.className = 'col-12 col-md-6 col-lg-4 parking-lot-card';
            
            col.innerHTML = `
                <div class="card bg-white dark-mode-card rounded shadow h-100">
                    <div class="card-header bg-white dark-mode-card border-bottom pt-4 pb-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="mb-0 text-primary dark-mode-text parking-lot-name">
                                <i class="fas fa-building me-2"></i>${lot.name}
                            </h5>
                            <span class="badge bg-primary price-badge">₹${lot.price_per_hour}/hr</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <!-- Location Details -->
                        <div class="location-details mb-4">
                            <p class="mb-2 dark-mode-text">
                            <i class="fas fa-map-marker-alt text-primary me-2"></i>
                                <span class="location-text">${lot.address}</span>
                        </p>
                            <p class="mb-0 dark-mode-text">
                                <i class="fas fa-map-pin text-primary me-2"></i>
                                <span class="pincode-text">${lot.pincode}</span>
                            </p>
                        </div>
                        
                        <!-- Availability Bar -->
                        <div class="availability-section mb-4">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="text-muted dark-mode-text">
                                    <i class="fas fa-car-side me-1"></i> Available Spots
                            </span>
                                <span class="fw-bold dark-mode-text">${lot.available_spots}</span>
                            </div>
                            <div class="availability-bar">
                                <div class="progress" style="height: 8px;">
                                    <div class="progress-bar bg-success" role="progressbar" 
                                        style="width: ${(lot.available_spots / 5) * 100}%"
                                        aria-valuenow="${lot.available_spots}" 
                                        aria-valuemin="0" 
                                        aria-valuemax="5">
                                    </div>
                                    <div class="progress-bar bg-danger" role="progressbar" 
                                        style="width: ${100 - (lot.available_spots / 5) * 100}%"
                                        aria-valuenow="${5 - lot.available_spots}" 
                                        aria-valuemin="0" 
                                        aria-valuemax="5">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer bg-transparent border-top-0 pt-0 pb-3">
                        ${lot.available_spots > 0 ? `
                            <button type="button" class="btn btn-primary w-100 lot-book-btn" 
                                data-lot-id="${lot.id}"
                                data-lot-name="${lot.name}"
                                data-address="${lot.address}"
                                data-pincode="${lot.pincode}"
                                data-price="${lot.price_per_hour}"
                                data-available-spots="${lot.available_spots}"
                                data-spot-ids="${lot.spot_ids.join(',')}">
                                <i class="fas fa-calendar-check me-2"></i>Book a Spot
                            </button>
                        ` : `
                            <button class="btn btn-secondary w-100" disabled>
                                <i class="fas fa-times-circle me-2"></i>No Available Spots
                        </button>
                        `}
                    </div>
                </div>
            `;
            
            return col;
        },

        reattachEventListeners() {
            document.querySelectorAll('.lot-book-btn').forEach(button => {
                button.addEventListener('click', async function () {
                    try {
                        // Always reset booking form before any check to avoid stale state
                        BookingModalHandler.resetForm();
                        bookModal.hide();
                
                        const hasActiveBooking = await BookingValidator.checkActiveBookings();
                
                        if (hasActiveBooking) {
                            const warningModal = new bootstrap.Modal(document.getElementById('activeBookingWarningModal'));
                            warningModal.show();
                
                            // Optionally bind cancel button here
                            document.getElementById('cancelBookingBtn')?.addEventListener('click', () => {
                                // Trigger cancel booking flow (redirect or modal)
                                window.location.href = '/cancel-booking'; // or trigger modal here
                            });
                
                            return;
                        }
                
                        if (!BookingValidator.isProfileComplete()) {
                            profileModal.show();
                            return;
                        }
                
                        // All checks passed, show booking modal
                        BookingModalHandler.updateModalContent(this);
                        bookModal.show();
                
                    } catch (error) {
                        console.error('Error during booking check:', error);
                        showErrorMessage('Error checking booking eligibility. Please try again.');
                        BookingModalHandler.resetForm();
                        bookModal.hide();
                    }
                });           
            });
        },

        showErrorMessage(message) {
            const container = document.getElementById('parkingLotsContainer');
            if (container) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-exclamation-circle fa-3x mb-3 text-danger"></i>
                        <h4 class="text-danger">Error</h4>
                        <p class="text-muted">${message}</p>
                    </div>
                `;
            }
        }
    };

    // Initialize the ParkingLotsManager
    ParkingLotsManager.initialize();

    // Add event listeners for book buttons
    document.querySelectorAll('.lot-book-btn').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Check for active bookings and profile completion
            const isEligible = await BookingValidator.validateBookingEligibility();
            if (!isEligible) {
                return;
            }
            
            // If eligible, proceed with booking modal
            BookingModalHandler.updateModalContent(this);
            bookModal.show();
        });
    });
    
    // Profile form submission
    const saveProfileBtn = document.getElementById('saveProfileBtn');
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', ProfileUpdateHandler.handleProfileUpdate);
    }
    
    // Booking form submission
    document.getElementById('bookingForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const isEligible = await BookingValidator.validateBookingEligibility();
        if (!isEligible) {
            bookModal.hide();
            BookingModalHandler.resetForm();
            return;
        }
        
        const formData = new FormData(this);
        try {
            const response = await fetch('/book_spot', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (result.success) {
                // Show success message
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
                successAlert.style.zIndex = '9999';
                successAlert.innerHTML = `
                    <i class="fas fa-check-circle me-2"></i>
                    ${result.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                document.body.appendChild(successAlert);
                
                // Redirect after a short delay
                setTimeout(() => {
                    window.location.href = '/user/dashboard';
                }, 1500);
            } else {
                showErrorMessage(result.message || 'Failed to book parking spot. Please try again.');
                bookModal.hide();
                BookingModalHandler.resetForm();
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorMessage('An error occurred while booking. Please try again.');
            bookModal.hide();
            BookingModalHandler.resetForm();
        }
    });

    // Handle modal hidden event to reset form
    document.getElementById('bookModal').addEventListener('hidden.bs.modal', function() {
        BookingModalHandler.resetForm();
    });
}); 