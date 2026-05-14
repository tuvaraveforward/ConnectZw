# Task: Reduce image sizes and show them on 4 columns

## Progress
- [x] 1. Create scripts/optimize_images.py
- [x] 2. Run optimization script 
- [x] 3. Update CSS in templates/Client/client-products.html for strict 4-column desktop grid + smaller images
- [x] 4. Update templates/Client/client_dashboard.html products-grid CSS
- [ ] 5. Test changes

## Commands to run after edits:
```
python manage.py collectstatic --noinput
python manage.py runserver
```
Visit http://127.0.0.1:8000/Client/products/grocery/ (login as client) to test 4-col smaller images.

