import requests
import json
from bs4 import BeautifulSoup
import sqlite3
from flask import Flask, render_template, request

app= Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/department')
def choose_department():
    dep_lst,types_lst=get_departments_types()
    lst=zip(dep_lst, types_lst)
    return render_template('department.html',lst=lst)

@app.route('/product',methods=['POST'])
def choose_product():
    type=request.form['type']
    product_lst=get_products(type)
    return render_template('product.html',product_lst=product_lst)

@app.route('/detail',methods=['POST'])
def choose_product():
    type=request.form['product']
    product_lst=get_products(type)
    return render_template('product.html',product_lst=product_lst)

# def get_results(sort_by, sort_order):
#     conn = sqlite3.connect('OP.sqlite')
#     cur = conn.cursor()
    
#     if sort_by == 'rating':
#         sort_column = 'Rating'
#     else:
#         sort_column = 'CocoaPercent'

#     q = f'''
#         SELECT SpecificBeanBarName, {sort_column}
#         FROM product
#         ORDER BY {sort_column} {sort_order}
#         LIMIT 10
#     '''
#     results = cur.execute(q).fetchall()
#     conn.close()
#     return results

# @app.route('/departments', methods=['POST'])
# def results():
#     sort_by = request.form['sort']
#     sort_order = request.form['dir']
#     results = get_results(sort_by, sort_order)
#     return render_template('results.html', 
#         sort=sort_by, results=results)
























base_url="https://www.optimumnutrition.com/"
CACHE_FILENAME='cache.txt'

#create a database
conn = sqlite3.connect('OP.sqlite',check_same_thread=False)
cur = conn.cursor()

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

def get_departments_types():
    ''' Get the product department anchor tag element list and type anchor tag  element list from html
    Print the department names with index and following type names
    
    Parameters
    ----------
    None
    
    Returns
    -------
    product_dep_lst: list
    product_types_lst :list
    '''
    html=make_request_with_cache(base_url)
    soup=BeautifulSoup(html, 'html.parser')
    menu=soup.find_all('ul',class_='menu-text')[0].find_all('li',recursive=False)
    product_dep_lst=[]
    product_types_lst=[]
    for i in menu:
        a=i.find_all('a')
        product_dep_lst.append(a[0])        
        product_types_lst.append(a[1:])
        # write value to table departments & types
        dep=a[0].text
        cur.execute(Insert_departments,[dep,dep])
        conn.commit()
        dep_id = cur.execute(f"SELECT department_id FROM Departments WHERE name='{dep}'").fetchall()[0][0]
        for i in a[1:]:
            type=i.text
            cur.execute(Insert_types,[type,dep_id,type])

    dep_print(product_dep_lst,product_types_lst)
    return product_dep_lst,product_types_lst

       

# get the products detail information from html#
def get_products(product_type):
    ''' Get the product detail information list from new html
    Print the product names with indexes
    
    Parameters
    ----------
    product_type: anchor tag element
    
    Returns
    -------
    product_lst: list
        a list contains product detail dictionaries
    '''
    
    product_type=BeautifulSoup(product_type, 'html.parser')
    product_type=product_type.find_all('a')[0]
    html=make_request_with_cache(base_url+product_type['href'])
    soup=BeautifulSoup(html, 'html.parser')
    products=soup.find_all('div', class_='views-row')
    product_lst=[]
    for p in products:
        dict={}
        a=p.contents[1].contents[1]
        name=a.find_all('h4')[0].text.strip()
        dict['name']=name
        dict['reason_to_use']=a.find_all('div',class_="field--name-field-reason-to-use-product")[0].text.strip()
        dict['lowest_price']=float(a.find_all('span', class_='acq-commerce-price')[0].contents[2].strip())
        dict['url']=a['href']
        rating_div=a.find_all('div', class_='pr-snippet-rating-decimal')
        if rating_div:
            dict['rating']=float(rating_div[0].text.strip())
        else:
            dict['rating']=""
        product_lst.append(dict)
    # product_print(product_type,product_lst)
    return product_lst

############################################## Pretty Print ######################################################

# def dep_print(product_dep_lst,product_types_lst):
#     ''' Print the departments with indexes and following types
    
#     Parameters
#     ----------
#     product_dep_lst: list
#         A list of department anchor tag element
#     product_types_lst
#         A list of lists of type anchor tag element

#     Returns
#     -------
#     None
#     '''
#     print("-----------------------------")
#     print(f"List of product departments")
#     print("-----------------------------")
#     idx=0
#     for d,t in zip(product_dep_lst,product_types_lst):
#         print("")
#         idx +=1
#         print(f'[{idx}] {d.text}')
#         for i in t:
#             print('  |',i.text)

# def type_print(product_dep,product_type_lst):
#     ''' Print the a department and its following types with indexes.
    
#     Parameters
#     ----------
#     product_dep: anchor tag element
#         A department 
#     product_type_lst
#         A list of type anchor tag element in one department

#     Returns
#     -------
#     None
#     '''
#     idx=0
#     print("----------------------------------")
#     print(f"List of product types in {product_dep.text}")
#     print("----------------------------------")
#     for a in product_type_lst:
#         idx += 1
#         print(f'[{idx}]{a.text}')
#     print("")
    
# def product_print(product_type,product_lst):
#     ''' Print the a product type and its following products with indexes.
    
#     Parameters
#     ----------
#     product_type: anchor tag element
#         A product type
#     product_lst:
#         A list of dictionaries of product detail information in one type

#     Returns
#     -------
#     None
#     '''
#     print("")
#     print("----------------------------------")
#     print(f"List of products in {product_type.text}")
#     print("----------------------------------")
#     idx=0
#     for p in product_lst:
#         idx += 1
#         name=p['name']
#         print (f'[{idx}] {name}')


# def detail_print(product_lst,product_i):
#     '''choose a product by index 
#     Pretty prints raw result
    
#     Parameters
#     ----------
#     product_lst:list
#         a list contains product detail dictionaries
#     product_i:int
#         an integer the user chooses

#     Returns
#     -------
#     None
#     '''
#     p=product_lst[product_i-1]
#     print("-------------------------------------------------------------------")
#     for i in p:
#         attr= '{:^22}'.format('{:.20}'.format(str(i)))
#         value = '{:^42}'.format('{:.40}'.format(str(p[i])))
        
#         print ("|"+attr+"|"+value+"|")
#     print("-------------------------------------------------------------------")

############################################## Input Validation ######################################################

def valid(num,lst):
    '''Validate the input.
        If the input is invalid, it will print the error message.
    
    Parameters
    ----------
    num:int
        An integer the user enters.
    lst: list
        The list of deparments/types/products to choose
    Returns
    -------
    num:int
        An valid integer the user chooses
    '''
    if num == 'exit':
            exit(0)
    elif num.isnumeric():
        num=int(num)
        if num >0 and num <= len(lst):
            return num
        else:
            print('[Error] Invalid input \n\n ----------------------------------')            
    else:
        print('[Error] Invalid input \n\n ----------------------------------')

############################################## Database ######################################################


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
        "lowest_price" NUMERIC NOT NULL,
        "url" TEXT NOT NULL UNIQUE,
        "rating" NUMERIC,
        "department_id" INTEGER REFERENCES Departments(department_id),
        "type_id" INTEGER REFERENCES Departments(type_id)
    );
"""

# Insert_products=""" 
#     INSERT INTO Products ('name','reason_to_use','lowest_price','url','rating','department_id','type_id')
#     VALUES(?,?,?,?,?,?,?)
# """
Insert_products=""" 
    INSERT INTO Products ('name','reason_to_use','lowest_price','url','rating','department_id','type_id')
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
    

   
def insert_tb_products(product_lst,product_dep,product_type):
    '''Insert the value to the table in database via sql
    
    Parameters
    ----------
    product_lst:list
        a list contains product detail information dictionaries

    Returns
    -------
    None
    '''

    for p in product_lst:
        lst=list(p.values())
        dep=product_dep.text
        type=product_type.text
        name=lst[0]
        dep_id=cur.execute(f"SELECT department_id FROM Departments WHERE name='{dep}'").fetchall()[0][0]
        type_id=cur.execute(f"SELECT type_id FROM Types WHERE name='{type}'").fetchall()[0][0]
        lst.append(dep_id)
        lst.append(type_id)
        lst.append(name)
        cur.execute(Insert_products,lst)
    conn.commit()



############################################## Loop ######################################################

def dep_choice_valid_or_exit():
    '''Ask the user to choose a number of deparments or exit.
        If the input is invalid, it will print the error message and ask for the input again.

        Print the departments with indexes and following types.
        Call the next step function to explore types.
    
    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    while True: 
        print("")
        num=input('Enter a index of departments or "exit": ')
        dep_i=valid(num,product_dep_lst)
        if dep_i:
            product_dep=product_dep_lst[dep_i-1]
            product_type_lst=product_types_lst[dep_i-1]
            type_print(product_dep,product_type_lst)
            type_choice_valid_or_exit_or_back(product_dep,product_type_lst)
        
def type_choice_valid_or_exit_or_back(product_dep,product_type_lst):
    '''Ask the user to choose a number of types or exit or back.
        If the input is invalid, it will print the error message and ask for the input again.
        If input is "back", back to the previous function to choose a department.
        If input is a valid number,
            Print the type with indexes.
            Call the next step function to explore products.
    
    Parameters
    ----------
    product_dep: anchor tag element
        A department 
    product_type_lst
        A list of type anchor tag element in one department

    Returns
    -------
    None
    '''

    while True: 
        print("")
        num=input('Enter a index of types or "exit" or "back": ')
        if num == 'back':
            dep_print(product_dep_lst,product_types_lst)
            dep_choice_valid_or_exit()
        else:
            type_i=valid(num,product_type_lst)
            if type_i:
                product_type=product_type_lst[type_i-1]
                product_lst=get_products(product_type)
                insert_tb_products(product_lst,product_dep,product_type)
                product_choice_valid_or_exit_or_back(product_lst,product_type_lst,product_dep)
                
def product_choice_valid_or_exit_or_back(product_lst,product_type_lst,product_dep):
    '''Ask the user to choose a number of products or exit or back.
        If the input is invalid, it will print the error message and ask for the input again.
        If input is "back", back to the previous function to choose a type.
        If input is a valid number,
            Print products with indexes.
            Call the self function to explore products again.
    
    Parameters
    ----------
    product_lst:list
        A list contains product detail dictionaries
    product_dep: anchor tag element
        A department 
    product_type_lst
        A list of type anchor tag element in one department
    product_type
        An anchor tag element in one department
    Returns
    -------
    None
    '''
    while True:  
        print("")
        num=input('Enter a index of products or "exit" or "back": ')
        if num == 'back':
            type_print(product_dep,product_type_lst)
            type_choice_valid_or_exit_or_back(product_dep,product_type_lst)
        else:
            product_i=valid(num,product_lst)
            if product_i:
                p=detail_print(product_lst,product_i)
                product_choice_valid_or_exit_or_back(product_lst,product_type_lst,product_dep)








    


if __name__ == "__main__":
    print('starting Flask app', app.name)
    app.run(debug=True)
    #create the table

    cur.execute("DROP TABLE IF EXISTS departments")
    cur.execute("DROP TABLE IF EXISTS types")
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute(create_departments)
    cur.execute(create_types)
    cur.execute(create_products)
    

    # product_dep_lst,product_types_lst=get_departments_types()
    # #start the loop
    # dep_choice_valid_or_exit()
    # #close the database
    # conn.close()