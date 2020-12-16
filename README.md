The interaction is run by the flask

Instruction steps:

1. Run "python app.py" in the console
2. Open the site "http://127.0.0.1:5000/"
3. Here is the homepage. Click the button "Start Searching"

4.  On the top is the navigation bar. The navigation bar is on every page except the homepage.
   "Home" is the homepage; 
    "Department" is the department page with types to select;
    "Products" lists all the products; 
    "Cart" stores the selected items.

5. Here is the department page.
   Select one of the ratio buttons and submit the form.

6. Here is the "product" page under a certain type; the type is encoded in the URL.
   Select one or more products, and click the "Add to Cart" button to add items to the cart.

7. click "Products" to see all the product items.
   Select one or more products, and click the "Add to Cart" button to add items to the cart.

8. Here is the "cart" page.
   Select one or more products, and click the "Delete from Cart" button to remove items from the cart.

9. On both the "products" and "cart" page, the user can sort items by category, price, or rating in descending or ascending order.



Package:
requests, BeautifulSoup, sqlite3, flask
