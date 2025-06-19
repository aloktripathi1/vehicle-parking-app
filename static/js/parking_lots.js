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
                // Set flag to show booking modal after profile completion
                sessionStorage.setItem('showBookingAfterProfile', 'true');
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
            document.getElementById('modalAddress').textContent = address;
            document.getElementById('modalPincode').textContent = `Pincode: ${pincode}`;
            document.getElementById('modalPrice').textContent = `₹${price}/hr`;
            // Set spot_id to first available spot
            const spotIds = button.dataset.spotIds ? button.dataset.spotIds.split(',').filter(Boolean) : [];
            document.getElementById('modalSpotId').value = spotIds[0] || '';
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
                    
                    // Check if this update was triggered from a booking attempt
                    const wasTriggeredFromBooking = document.querySelector('#profileModal').classList.contains('show') || 
                                                  sessionStorage.getItem('showBookingAfterProfile') === 'true';
                    
                    if (wasTriggeredFromBooking && BookingValidator.isProfileComplete()) {
                        // Clear the flag
                        sessionStorage.removeItem('showBookingAfterProfile');
                        
                        setTimeout(() => {
                            editProfileModal.hide();
                            // Get the last clicked booking button
                            const lastClickedBtn = document.querySelector('.lot-book-btn[data-last-clicked="true"]');
                            if (lastClickedBtn) {
                                BookingModalHandler.updateModalContent(lastClickedBtn);
                                lastClickedBtn.removeAttribute('data-last-clicked');
                                setTimeout(() => bookModal.show(), 500);
                            }
                        }, 1500);
                    } else {
                        // Just close the edit profile modal after success
                        setTimeout(() => {
                            editProfileModal.hide();
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
    
    // Add event listeners for book buttons
    document.querySelectorAll('.lot-book-btn').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Store this button as the last clicked one
            document.querySelectorAll('.lot-book-btn').forEach(btn => btn.removeAttribute('data-last-clicked'));
            this.setAttribute('data-last-clicked', 'true');
            
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
            const response = await fetch('/user/book_spot', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            if (result.success) {
                // Hide modal immediately without animation
                bookModal.hide();
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
                
                // Show success message and redirect immediately
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
                successAlert.style.zIndex = '9999';
                successAlert.innerHTML = `
                    <i class="fas fa-check-circle me-2"></i>
                    ${result.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                document.body.appendChild(successAlert);
                
                // Redirect immediately
                window.location.href = '/user/dashboard';
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

    // Spot Status Modal Handler
    function setupSpotStatusModals() {
        document.querySelectorAll('[id^="checkSpotsModal"]').forEach(modalEl => {
            const lotId = modalEl.id.replace('checkSpotsModal', '');
            const modal = new bootstrap.Modal(modalEl);
            const button = document.querySelector(`[data-bs-target="#checkSpotsModal${lotId}"]`);
            if (button) {
                button.addEventListener('click', function() {
                    // Show loading spinner
                    document.getElementById(`spotsTableBody${lotId}`).innerHTML = `<tr><td colspan="2" class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></td></tr>`;
                    document.getElementById(`availableSpotsCount${lotId}`).textContent = '-';
                    document.getElementById(`totalSpotsCount${lotId}`).textContent = '-';
                    // Fetch spot data
                    fetch(`/api/parking_lot/${lotId}/spots`).then(r => r.json()).then(data => {
                        if (data.success) {
                            const spots = data.data.spots;
                            const available = spots.filter(s => s.status === 'A').length;
                            document.getElementById(`availableSpotsCount${lotId}`).textContent = available;
                            document.getElementById(`totalSpotsCount${lotId}`).textContent = spots.length;
                            const tbody = document.getElementById(`spotsTableBody${lotId}`);
                            tbody.innerHTML = '';
                            spots.forEach(spot => {
                                const row = document.createElement('tr');
                                row.innerHTML = `<td>${spot.id}</td><td>${spot.status === 'A' ? 'Available' : 'Occupied'}</td>`;
                                tbody.appendChild(row);
                            });
                        } else {
                            document.getElementById(`spotsTableBody${lotId}`).innerHTML = '<tr><td colspan="2" class="text-center text-danger">Failed to load spot data</td></tr>';
                        }
                    }).catch(() => {
                        document.getElementById(`spotsTableBody${lotId}`).innerHTML = '<tr><td colspan="2" class="text-center text-danger">Failed to load spot data</td></tr>';
                    });
                });
            }
        });
    }
    // Call the setup function after DOMContentLoaded
    setupSpotStatusModals();

    // Simple search and sort for Available Parking Lots
    const container = document.getElementById('parkingLotsContainer');
    if (!container) return;

    // Store original lots
    const originalLots = Array.from(container.children);

    // Create search and sort UI
    const searchRow = document.createElement('div');
    searchRow.className = 'row mb-4';
    searchRow.innerHTML = `
        <div class="col-md-6 mb-2">
            <input type="text" class="form-control w-100" id="searchInput" placeholder="Search by name or pincode..." style="max-width: 300px;">
        </div>
        <div class="col-md-6 mb-2 d-flex justify-content-end">
            <select class="form-select w-100" id="sortSelect" style="max-width: 300px;">
                <option value="price-asc">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
                <option value="spots">Availability: Most to Least</option>
            </select>
        </div>
    `;
    container.parentNode.insertBefore(searchRow, container);

    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');

    function filterAndSortLots() {
        let lots = Array.from(originalLots);
        const search = searchInput.value.trim().toLowerCase();
        if (search) {
            lots = lots.filter(card => {
                const name = card.querySelector('.parking-lot-name').textContent.toLowerCase();
                const pincode = card.querySelector('.pincode-text').textContent.toLowerCase();
                return name.includes(search) || pincode.includes(search);
            });
        }
        // Sort
        if (sortSelect.value === 'price-asc') {
            lots.sort((a, b) => getPrice(a) - getPrice(b));
        } else if (sortSelect.value === 'price-desc') {
            lots.sort((a, b) => getPrice(b) - getPrice(a));
        } else if (sortSelect.value === 'spots') {
            lots.sort((a, b) => getSpots(b) - getSpots(a));
        }
        // Render
        container.innerHTML = '';
        lots.forEach(card => container.appendChild(card));
    }
    function getPrice(card) {
        const priceText = card.querySelector('.price-badge').textContent;
        return parseFloat(priceText.replace(/[^\d.]/g, '')) || 0;
    }
    function getSpots(card) {
        const spotsText = card.querySelector('.fw-bold.dark-mode-text').textContent;
        return parseInt(spotsText) || 0;
    }
    searchInput.addEventListener('input', filterAndSortLots);
    sortSelect.addEventListener('change', filterAndSortLots);
}); 