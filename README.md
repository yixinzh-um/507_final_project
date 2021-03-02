**Website Scraping and Flask Application** 

(Python, SQL, Flask, HTML)

●	Extracted product information scraping from website and its inner page or cache.

●	Transformed and loaded records into three tables into a relational database. 

●	Navigated users by navigation bar or the radio button of the department. 

●	Sorted lists by the dropdown menu of category, price, or rating. 

●	Added adding to cart function; display or delete selected products in cart page via a checkbox. 





The interaction is run by the flask


**Package:**

requests, BeautifulSoup, sqlite3, flask


**Instruction steps:**

1.Run "python app.py" in the console

2.Open the site "http The number of records ranges from 0 to 45.://127.0.0.1:5000/"

3.Here is the homepage. Click the button "Start Searching"

4.On the top is the navigation bar. The navigation bar is on every page except the homepage.
    "Home" is the homepage; (“/”)
    "Department" is the department page with types to select; (“/department”)
    "Products" lists all the products; (“/products”)
    "Cart" stores the selected items. (“/cart”)

5.After step 3, here is the department page. (“/department”)
    Select one of the ratio buttons and submit the form.

6.Here is the "product" page under a certain type; the type is encoded in the URL.(“ /type/<type>”)
    Select one or more products and click the "Add to Cart" button to add items to the cart.

7.Click "Products" on the top navigation bar to see all the product items. (“/products”)
    Select one or more products and click the "Add to Cart" button to add items to the cart.

8.Here is the "cart" page. (“/cart”) 
    Select one or more products and click the "Delete from Cart" button to remove items from the cart.

9.On both the "products" and "cart" page, the user can sort items by category, price, or rating in descending or ascending order.


Demo link:
https://drive.google.com/file/d/1_mXrcuwtN395V7KyEXL3LDVevedAsu9V/view?usp=sharing

