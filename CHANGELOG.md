# Changelog

## Latest Changes

### Database Schema Changes
- **Removed Admin Model**: Merged `Admin` class into `User` class
- **Added Role Field**: Users now have a `role` field ('user' or 'admin') instead of separate tables
- **Migration**: Existing admin users automatically migrated from `admins` table to `users` table

### Route Organization
- **Removed API Blueprint**: API routes moved to their respective role directories
- **Admin API Routes** (in `routes/admin/`):
  - admin_user_reservations.py
  - parking_lot_spots.py
  - parking_lots.py
  - parking_stats.py
  - search_users.py
- **User API Routes** (in `routes/user/`):
  - book_parking.py
  - check_active_booking.py
  - user_reservations.py
  - parking_lot_user.py

### Authentication Changes
- **Unified Login**: Single login endpoint for both users and admins
- **Role-Based Routing**: Users redirected based on their role after login
- **Session Management**: User role stored in session as `user_type`

### Admin User Creation
- **Programmatic Creation**: Admin user automatically created on app startup
- **Environment Variables**: Configurable via:
  - `ADMIN_EMAIL` (default: admin@parkease.com)
  - `ADMIN_PASSWORD` (default: admin123)
  - `ADMIN_NAME` (default: Admin User)
- **No Registration**: Admin users cannot register through the UI

### Code Improvements
- Simplified user authentication logic
- Removed duplicate code between User and Admin models
- Cleaner blueprint organization
- Better separation of concerns

### Default Credentials
- Email: admin@parkease.com
- Password: admin123

**Note**: Change default admin credentials via environment variables in production.
