import mysql.connector as sql
from tabulate import tabulate
import time
#a. function to view usernames
def view_unames():
    cur.execute('select u_id,fname,lname from users_m')
    data=cur.fetchall()
    head=['User ID','First Name','Last Name']
    print(tabulate(data,tablefmt='fancy_grid',headers=head))
    
#b. function to view all products
def view_pnames():
    cur.execute('select p_id,p_name,c_name from products,categories_m where products.c_id=categories_m.c_id')
    data=cur.fetchall()
    head=['Product ID','Product Name','Category']
    print(tabulate(data,tablefmt='fancy_grid',headers=head))

#c. function to view all product locations
def view_locs():
    cur.execute('select distinct location from reviews')
    data=cur.fetchall()
    head=['Location']
    print(tabulate(data,tablefmt='fancy_grid',headers=head))

#d. function to view all categories
def view_cnames():
    cur.execute('select c_id,c_name from categories_m')
    data=cur.fetchall()
    head=['Category ID','Category Name']
    print(tabulate(data,tablefmt='fancy_grid',headers=head))

#1. function to add a review
def add_review():
    cur.execute('select count(*) from reviews')
    nr=int(cur.fetchone()[0])
    rev_id=nr+1
    name=input('Enter first name:')
    cur.execute('select u_id from users_m where fname="{}"'.format(name))
    try:
        u_id=int(cur.fetchone()[0])
    except:
        print('User not found')
        return
    prod=input('Enter product:')
    cur.execute('select p_id from products where p_name="{}"'.format(prod))
    try:
        p_id=int(cur.fetchone()[0])
    except:
        print('Product not found')
        return
    location=input('Enter location:')
    review=input('Enter review:')
    rating=input('Enter rating? If not rating enter NULL:')
    if rating.lower()=='null':
        cur.execute('insert into reviews values ({},{},{},"{}","{}",NULL,{},{},"{}")'.format(rev_id,u_id,p_id,location,review,rev_id,rev_id,'ACTIVE'))
    else:
        if float(rating)>5:
            print('Invalid rating')
            return
        cur.execute('insert into reviews values ({},{},{},"{}","{}",{},{},{},"{}")'.format(rev_id,u_id,p_id,location,review,rating,rev_id,rev_id,'ACTIVE'))        
    con.commit()
    
#2. function to view reviews of a product
def view_prod():
    p_name=input('Enter name of product:')
    cur.execute('select p_id from products where p_name="{}"'.format(p_name))
    try:
        p_id=int(cur.fetchone()[0])
    except:
        print('No records found')
        return
    cur.execute('select fname,lname,p_name,reviews.location,rev_id,review,rating,parent_rev_id,thread_id from reviews,users_m,products where users_m.u_id=reviews.u_id and products.p_id=reviews.p_id and products.p_id={}'
.format(p_id))
    data=cur.fetchall()
    head=['First Name','Last Name','Product Name','Location','Review ID','Review','Rating','Parent Review','Thread ID']
    print(tabulate(data,tablefmt='fancy_grid',headers=head, maxcolwidths=[None,None,None,None,None,20,None,None,None]))
    cur.execute('select avg(rating) from reviews where p_id={}'.format(p_id))
    avg=cur.fetchall()[0][0]
    print('Average rating:',avg)

#3. function to view reviews for a location
def view_loc():
    location=input('Enter location:')
    cur.execute('select fname,lname,p_name,reviews.location,rev_id,review,rating,parent_rev_id,thread_id from reviews,users_m,products where users_m.u_id=reviews.u_id and products.p_id=reviews.p_id and reviews.location="{}"'
.format(location))
    data=cur.fetchall()
    if data==[]:
        print('No records found')
    else:
        head=['First Name','Last Name','Product Name','Location','Review ID','Review','Rating','Parent Review','Thread ID']
        print(tabulate(data,tablefmt='fancy_grid',headers=head, maxcolwidths=[None,None,None,None,None,20,None,None,None]))
        
#4. function to view all reviews by a person
def view_user():
    fname=input('Enter the first name of user whose reviews you wish to see:')
    cur.execute('select u_id from users_m where fname="{}"'.format(fname))
    try:
        u_id=int(cur.fetchone()[0])
    except:
        print('No records found')
        return
    cur.execute('select fname,lname,p_name,reviews.location,rev_id,review,rating,parent_rev_id,thread_id from reviews,users_m,products where users_m.u_id=reviews.u_id and products.p_id=reviews.p_id and reviews.u_id={}'
.format(u_id))
    data=cur.fetchall()
    if data==[]:
        print('No records found')
        return
    head=['First Name','Last Name','Product Name','Location','Review ID','Review','Rating','Parent Review','Thread ID']
    print(tabulate(data,tablefmt='fancy_grid',headers=head, maxcolwidths=[None,None,None,None,None,20,None,None,None]))

#5. function to view all reviews by a user's particular category of relatives
def view_rel():
    fname=input('Enter first name of person whose relations you wish to view:')
    cur.execute('select u_id from users_m where fname="{}"'.format(fname))
    try:
        u_id=int(cur.fetchone()[0])
    except:
        print('No records found')
        return
    rel=input('Enter relation - family, friends, married:')
    if rel.lower() not in ['family','friends','married']:
        print('Wrong input')
        return
    cur.execute('select * from relations_m where (u1={} or u2={}) and relation="{}"'.format(u_id,u_id,rel))
    data=cur.fetchall()
    if data==[]:
        print('No records found')
        return
    rels=[0]
    for i in data:
        if i[1]==u_id:
            rels.append(i[2])
        else:
            rels.append(i[1])
    rels=tuple(rels)
    query='select fname,lname,p_name,reviews.location,rev_id,review,rating,parent_rev_id,thread_id from reviews,users_m,products where users_m.u_id=reviews.u_id and products.p_id=reviews.p_id and reviews.u_id in {}'.format((rels))
    cur.execute(query)
    data=cur.fetchall()
    if data==[]:
        print('No records found')
        return
    head=['First Name','Last Name','Product Name','Location','Review ID','Review','Rating','Parent Review','Thread ID']
    print("Reviews by ",fname,"'s ",rel,sep='')
    print(tabulate(data,tablefmt='fancy_grid',headers=head, maxcolwidths=[None,None,None,None,None,20,None,None,None]))

#6. view all records of a category
def view_cat():
    c_name=input('Enter category:')
    cur.execute('select c_id from categories_m where c_name="{}"'.format(c_name))
    try:
        c_id=int(cur.fetchone()[0])
    except:
        print('No matching category found')
        return
    cur.execute('select distinct fname,lname,p_name,reviews.location,rev_id,review,rating,parent_rev_id,thread_id from reviews,users_m,products,categories_m where users_m.u_id=reviews.u_id and products.p_id=reviews.p_id and categories_m.c_id=products.c_id and categories_m.c_id={}'
.format(c_id))
    data=cur.fetchall()
    if data==[]:
        print('No records')
        return
    head=['First Name','Last Name','Product Name','Location','Review ID','Review','Rating','Parent Review','Thread ID']
    print(tabulate(data,tablefmt='fancy_grid',headers=head, maxcolwidths=[None,None,None,None,None,20,None,None,None]))

#7. Deactivate a thread
def deactivate():
    t_id=int(input('Enter thread id to deactivate:'))
    cur.execute('update reviews set status="INACTIVE" where thread_id={}'.format(t_id))
    con.commit()
    
con=sql.connect(host='localhost',user='root',passwd='root@123',database='csc2025')
cur=con.cursor()
while True:
    print('ENTER YOUR CHOICE:')
    print('a. View all users\nb. View all products\nc. View all product locations\nd. View all categories')
    print("1. Add a new review\n2. View all reviews of a product\n3. View all reviews for a location\n4. View all reviews posted by a person\n5. View all reviews from a person's specific category of relatives\n6. View all reviews of a particular category\n7. Deactivate a thread")
    ch=input('Enter your choice:')
    if ch.lower()=='a':
        view_unames()

    elif ch.lower()=='b':
        view_pnames()
        
    elif ch.lower()=='c':
        view_locs()

    elif ch.lower()=='d':
        view_cnames()

    elif ch=='1':
        add_review()
        
    elif ch=='2':
        view_prod()

    elif ch=='3':
        view_loc()

    elif ch=='4':
        view_user()
            
    elif ch=='5':
        view_rel()

    elif ch=='6':
        view_cat()
        
    elif ch=='7':
        deactivate()

    else:
        print('Terminating')
        break
    
    time.sleep(2)
    print('-'*75)



