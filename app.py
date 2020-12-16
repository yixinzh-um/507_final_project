import requests
import json
from bs4 import BeautifulSoup
import sqlite3
from flask import Flask, render_template, request


base_url="https://www.optimumnutrition.com/"
CACHE_FILENAME='cache.txt'
conn = sqlite3.connect('OP.sqlite',check_same_thread=False)
cur = conn.cursor()


app= Flask(__name__)

@app.route('/')
def index():
    ''' homepage
    
    Parameters
    ----------
    None
    
    Returns
    -------
    htmle
    '''
    return render_template('index.html')

@app.route('/department')
def choose_department():
    ''' department and type page; choose a certain type to explore the products under it
    
    Parameters
    ----------
    None
    
    Returns
    -------
    html
    '''
    dep_lst,types_lst=get_dep_types()
    lst=zip(dep_lst, types_lst)
    return render_template('department.html',lst=lst)

@app.route('/type/<type>',methods=['POST'])
def choose_product(type):
    ''' products under certain types page;
    choose one or more products added to the cart
    
    Parameters
    ----------
    type
    
    Returns
    -------
    html
    '''
    type=request.form['type']
    product_lst=get_products_by_type(type)
    return render_template('product.html',product_lst=product_lst,type=type)

@app.route('/products', methods=['GET','POST'])
def products_all():
    ''' products page lists all the 45 records;
    choose one or more products added to the cart
    
    Parameters
    ----------
    None
    
    Returns
    -------
    html
    '''
    sort_by='Category'
    sort_order='ASC'
    try:
        sort_by = request.form['sort']
        sort_order = request.form['dir']
    except:
        pass
    product_lst=get_all_products(sort_by, sort_order)
    return render_template('products_all.html',product_lst=product_lst,sort_by=sort_by,sort_order=sort_order)



@app.route('/cart', methods=['GET','POST'])
def cart():
    ''' cart page;
    delete one or more products from the cart
    
    Parameters
    ----------
    None
    
    Returns
    -------
    html
    '''
    sort_by='Category'
    sort_order='ASC'
    try:
        sort_by = request.form['sort']
        sort_order = request.form['dir']
    except:
        pass

    cart_lst=[]

    product_id_lst=request.form.getlist('product')
    drop_product_id_lst=request.form.getlist('cart')
    
    if product_id_lst:
        write_cart(product_id_lst)
    if drop_product_id_lst:
        drop_cart(drop_product_id_lst)

    print(drop_product_id_lst)
    cart_lst=read_cart(sort_by, sort_order)
    return render_template('cart.html',product_lst=cart_lst,sort_by=sort_by,sort_order=sort_order)



############################################## Caching & Request ######################################################
def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def make_request_with_cache(url):
    '''Check the cache for a saved result for this state. 
    If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    If the result is in your cache, print "Using Cache"
    If request a new result using get_sites_for_state(state_url), print "Fetching"

    Parameters
    ----------
    url: string
    
    Returns
    -------
    result: html string
    '''
    dict=open_cache()
    if url not in dict:
        print("Fetching")
        response=requests.get(url)
        result=response.text
        dict[url]=result     
        save_cache(dict)
    else:
        print("Using Cache")
        result=dict[url]
    return result

############################################## BeautifulSoup ######################################################

def wirte_to_database():
    ''' Get the product department anchor tag element list and type anchor tag  element list from html
    Write departments and types into the table Departments and Types in database.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''

    cur.execute("DROP TABLE IF EXISTS departments")
    cur.execute("DROP TABLE IF EXISTS types")
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("DROP TABLE IF EXISTS cart")
    cur.execute(create_departments)
    cur.execute(create_types)
    cur.execute(create_products)
    cur.execute(create_cart)

    html=make_request_with_cache(base_url)
    soup=BeautifulSoup(html, 'html.parser')
    menu=soup.find_all('ul',class_='menu-text')[0].find_all('li',recursive=False)
    for i in menu:
        a=i.find_all('a')
        # write value to table departments & types
        dep=a[0].text
        
        cur.execute(Insert_departments,[dep,dep])
        dep_id = cur.execute(f"SELECT department_id FROM Departments WHERE name='{dep}'").fetchall()[0][0]
        for i in a[1:]:
            type=i.text
            cur.execute(Insert_types,[type,dep_id,type])
            type_id=cur.execute(f"SELECT type_id FROM Types WHERE name='{type}'").fetchall()[0][0]
            product_lst=get_products(i)
            insert_tb_products(product_lst,dep_id,type_id)
    conn.commit()
    conn.close()

     

# get the products detail information from html#
def get_products(product_type):
    ''' Get the product detail information list from new html
    Print the product names with indexes
    
    Parameters
    ----------
    product_type: anchor tag element
    
    Returns
    -------
    lst: list
        a list contains product dictionaries
    '''

    html=make_request_with_cache(base_url+product_type['href'])
    soup=BeautifulSoup(html, 'html.parser')
    products=soup.find_all('div', class_='views-row')[1:]
    lst=[]
    for p in products: 
        dict={}
        a=p.contents[1].contents[1]
        dict['name']=a.find_all('h4')[0].text.strip()
        dict['reason_to_use']=a.find_all('div',class_="field--name-field-reason-to-use-product")[0].text.strip()
        dict['price_from']=float(a.find_all('span', class_='acq-commerce-price')[0].contents[2].strip())
        dict['url']=a['href']
        rating_div=a.find_all('div', class_='pr-snippet-rating-decimal')
        if rating_div:
            dict['rating']=float(rating_div[0].text.strip())
        else:
            dict['rating']=None
        lst.append(dict)
    return lst
    
class product:
    '''A product item with its six attributes!
    '''
    def __init__(self,id,name, reason_to_use, price_from, url, rating,type=None):    
        self.id=id
        self.name=name
        self.reason_to_use=reason_to_use
        self.price_from=price_from
        self.url=url
        self.rating=rating
        self.type = type




############################################## Database after scraping ######################################################


# Write to database #
create_departments=""" 
    CREATE TABLE IF NOT EXISTS "Departments" (
        "department_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "name" TEXT NOT NULL UNIQUE
    );
"""
create_types=""" 
    CREATE TABLE IF NOT EXISTS "Types" (
        "type_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "name" TEXT NOT NULL UNIQUE,
        "department_id" INTEGER REFERENCES Departments(department_id)
    );
"""
create_products=""" 
    CREATE TABLE IF NOT EXISTS "Products" (
        "product_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "name" TEXT NOT NULL UNIQUE,
        "reason_to_use" TEXT NOT NULL,
        "price_from" NUMERIC NOT NULL,
        "url" TEXT NOT NULL UNIQUE,
        "rating" NUMERIC,
        "department_id" INTEGER REFERENCES Departments(department_id),
        "type_id" INTEGER REFERENCES Departments(type_id)
    );
"""
create_cart="""
    CREATE TABLE IF NOT EXISTS "Cart" (
        "cart_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "name" TEXT NOT NULL UNIQUE,
        "product_id" INTEGER REFERENCES products(product_id)
    );
"""


Insert_cart=""" 
    INSERT INTO Cart ('name','product_id')
    SELECT ?,?
    WHERE NOT EXISTS (select * from cart where product_id=?)
"""

Insert_products=""" 
    INSERT INTO Products ('name','reason_to_use','price_from','url','rating','department_id','type_id')
    SELECT ?,?,?,?,?,?,?
    WHERE NOT EXISTS (select * from Products where name=?)

"""

Insert_types="""INSERT INTO Types ('name','department_id')
                        SELECT ?,?
                        WHERE NOT EXISTS (SELECT * FROM Types WHERE name=?)  

                        """


Insert_departments="""INSERT INTO Departments ('name') 
                        SELECT ? 
                        WHERE NOT EXISTS (SELECT * FROM Departments WHERE name=?)
                        """
    

   
def insert_tb_products(product_lst,dep_id,type_id):
    '''Insert the value to the table in database via sql
    
    Parameters
    ----------
    product_lst:list
        a list contains product objects with detail information d

    Returns
    -------
    None
    '''

    for p in product_lst:
        lst=list(p.values())
        name=lst[0]
        lst.append(dep_id)
        lst.append(type_id)
        lst.append(name)
        cur.execute(Insert_products,lst)
    conn.commit()

############################################## Database for display & table Cart ######################################################

def write_cart(product_id_lst):
    '''Insert the value to the table Cart in database via sql
    
    Parameters
    ----------
    product_id_lst:list
        a list contains product id

    Returns
    -------
    None
    '''

    conn = sqlite3.connect('OP.sqlite')
    cur = conn.cursor()
    ##read from table products
    product_id_lst=[f"'{i}'" for i in product_id_lst]
    products_id=",".join(product_id_lst)
    q = f'''
        SELECT *
        FROM Products
        WHERE product_id in ({products_id})
    '''
    product_lst = cur.execute(q).fetchall()
    ##write to table cart
    for i in product_lst:
        lst=[i[1],i[0],i[0]]  
        cur.execute(Insert_cart,lst)
    conn.commit()
    conn.close()

def drop_cart(drop_product_id_lst):
    '''DELETE the row from the table Cart in database via sql
    
    Parameters
    ----------
    drop_product_id_lst:list
        a list contains product id

    Returns
    -------
    None
    '''
    conn = sqlite3.connect('OP.sqlite')
    cur = conn.cursor()
    ##delete row in table products
    product_id_lst=[f"{i}" for i in drop_product_id_lst]
    products_id=",".join(product_id_lst)
    q = f'''
        DELETE 
        FROM cart
        WHERE product_id in ({products_id})
    '''
    cur.execute(q).fetchall()
    conn.commit()
    conn.close()


def read_cart(sort_by, sort_order):
    '''read the data from the table Cart in database via sql and get list of product objects in cart
    
    Parameters
    ----------
    sort_by:string
        Category, Rating, or Price
    sort_order: string
        ASC, DESC

    Returns
    -------
    cart_lst:list
        a list contains product objects
    '''

    conn = sqlite3.connect('OP.sqlite')
    cur = conn.cursor()
    ##read from table cart
    if sort_by == 'Rating':
        sort_column = 'rating'
    elif sort_by=='Price':
        sort_column='price_from'
    elif sort_by == 'Category':
        sort_column = 'type_id'


    q = f'''
        SELECT products.*, types.name as type
        FROM cart
        JOIN Products on cart.product_id=products.product_id
        JOIN types ON types.type_id=products.type_id
        ORDER BY {sort_column} {sort_order} 
        NULLS LAST
    '''
    print(q)
    carts = cur.execute(q).fetchall()

    cart_lst=[]
    for i in carts:
        cart_lst.append(product(i[0],i[1],i[2],i[3],i[4],i[5],i[-1]))
        

    conn.commit()
    conn.close()
    return cart_lst


def get_dep_types():
    '''read the data from the table Departments and Types
    
    Parameters
    ----------
    None

    Returns
    -------
    dep_lst:list
        a list contains department names
    types_lst:list
        a list contains type names
    '''
    conn = sqlite3.connect('OP.sqlite')
    cur = conn.cursor()
    q1 = f'''
        SELECT name
        FROM Departments 
    '''
    dep_lst = cur.execute(q1).fetchall()
    types_lst=[]

    for i in range(len(dep_lst)):
        q2=f"""
        SELECT name
        FROM Types
        WHERE department_id='{i+1}'
        """
        type_lst = cur.execute(q2).fetchall()
        type_lst=[i[0] for i in type_lst]
        types_lst.append(type_lst)

    conn.close()
    return dep_lst,types_lst

def get_products_by_type(type):
    '''read the data from the table Products
    
    Parameters
    ----------
    type:string
        a type name returned from a request form

    Returns
    -------
    lst:list
        a list of product objects under specific type
    '''
    conn = sqlite3.connect('OP.sqlite')
    cur = conn.cursor()
    q = f'''
        SELECT * FROM Products 
        JOIN Types ON Products.type_id=Types.type_id
        WHERE Types.name='{type}'
    '''
    product_lst = cur.execute(q).fetchall()
    lst=[]
    for p in product_lst:
        product_object=product(p[0],p[1], p[2],p[3],p[4],p[5])
        lst.append(product_object)
    conn.close()
    return lst

def get_all_products(sort_by, sort_order):
    '''read the data from the table Products
    
    Parameters
    ----------
    sort_by:string
        Category, Rating, or Price
    sort_order: string
        ASC, DESC

    Returns
    -------
    lst:list
        a list contains all the sorted product objects
    '''
    conn = sqlite3.connect('OP.sqlite')
    cur = conn.cursor()

    if sort_by == 'Rating':
        sort_column = 'rating'
    elif sort_by=='Price':
        sort_column='price_from'
    elif sort_by == 'Category':
        sort_column = 'type_id'

    q = f'''
        SELECT Products.*, types.name as type 
        FROM Products
        JOIN types ON types.type_id=products.type_id
        ORDER BY {sort_column} {sort_order} 
        NULLS LAST
    '''
    product_lst = cur.execute(q).fetchall()
    lst=[]
    for p in product_lst:
        product_object=product(p[0],p[1], p[2],p[3],p[4],p[5],p[-1])
        lst.append(product_object)
    conn.close()
    return lst













if __name__ == "__main__":
    wirte_to_database()

    print('starting Flask app', app.name)
    app.run(debug=True)
