# Box Cricket Booking

This is a simple Django project for booking box cricket courts.

Quick start (Windows):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata booking/fixtures/initial_data.json
python manage.py createsuperuser
python manage.py runserver
```

Routes:
- `/` Homepage
- `/signup/` Signup
- `/login/` Login
- `/logout/` Logout
- `/profile/` User profile
- `/booking/` My bookings (requires login)
- `/booking/create/` Create booking (requires login)
- `/booking/venues/` Browse venues
- `/booking/venues/<id>/` Venue detail

Next steps:
- Add payment integration if required
- Improve availability checks and add calendar view
- Add unit tests and CI pipeline
