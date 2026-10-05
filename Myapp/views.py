import random

from django.shortcuts import render,redirect

from django.http import HttpResponse

from django.core.mail import EmailMessage

from django.db import connections

def shop(request):
    return render(request,"shop.html")

def home(request):
    return render(request,"add.html")

def ins(request):
    n=request.POST['nm']
    e=request.POST['email']
    dob=request.POST['dob']
    gender=request.POST['gender']
    stream=request.POST['stream']
    pas=request.POST['pass']
    fl=request.FILES['simg']
    with open("static/stdimg/"+fl.name,"wb+") as destination:
        for chunk in fl.chunks():
            destination.write(chunk)

    otp=random.randint(100000,999999)

    email=EmailMessage(
        subject='Python test',
        body='<h1>I am email body. Your otp is '+str(otp)+'</h1>',
        from_email='soumyahazra17@gmail.com',
        to=[e]
    )
    email.content_subtype="html"
    email.send()
    return HttpResponse(n+"<br/>"+e+"<br/>"+dob+"<br/>"+gender+"<br/>"+stream+"<br/>"+pas)

def about(request):
    return HttpResponse("I am Soumya")


def dashboard(request):
    return render(request,"dashboard.html")

def addproduct(request):
    return render(request,"addproduct.html")

def insproduct(request):
    cursor=connections['default'].cursor()
    pn=request.POST['pname']
    pp=request.POST['pprice']
    pb=request.POST['barcode']
    fl=request.FILES['pimg']
    with open("static/product_img/"+fl.name,"wb+") as destination:
        for chunk in fl.chunks():
            destination.write(chunk)

    sql_ins="INSERT INTO products SET product_name='"+str(pn)+"',product_price='"+str(pp)+"',product_img='"+str(fl.name)+"',product_barcode='"+str(pb)+"'"

    cursor.execute(sql_ins)      
    return redirect("/listproducts/")

def listproducts(request):
    cursor=connections['default'].cursor()
    sql="SELECT * FROM products";
    cursor.execute(sql)
    myproduct=cursor.fetchall()
    return render(request,"listproducts.html",{'pro':myproduct})

def deleteproduct(request, pid):
    cursor = connections['default'].cursor()
    delp = "DELETE FROM products WHERE product_id='" + str(pid) + "'"
    cursor.execute(delp)
    return redirect("/listproducts/")
# ----------------- CUSTOMER MANAGEMENT -----------------
def addcustomer(request):
    return render(request, "addcustomer.html")

def inscustomer(request):
    cursor = connections['default'].cursor()
    cn = request.POST['cname']
    cp = request.POST['cphone']
    cursor.execute("INSERT INTO customers (customer_name, customer_phone) VALUES (%s, %s)", [cn, cp])
    return redirect("/listcustomer/")

def listcustomer(request):
    cursor = connections['default'].cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    return render(request, "listcustomer.html", {'customers': customers})

# ----------------- CUSTOMER AUTHENTICATION -----------------
def customerlogin(request):
    if 'customer_id' in request.session:
        return redirect("/shop/")
    return render(request, "customerlogin.html")

def checkcustomerlogin(request):
    if request.method == "POST":
        email = request.POST.get('cemail')
        password = request.POST.get('cpassword')

        cursor = connections['default'].cursor()
        cursor.execute("SELECT customer_id, customer_name, customer_email FROM customers WHERE customer_email=%s AND customer_password=%s", [email, password])
        cust = cursor.fetchone()

        if cust:
            # Store customer details in session
            request.session['customer_id'] = cust[0]
            request.session['customer_name'] = cust[1]
            request.session['customer_email'] = cust[2]
            return redirect("/shop/")
        else:
            return render(request, "customerlogin.html", {'error': 'Invalid Email or Password'})

    return redirect("/customerlogin/")

def customerlogout(request):
    # Clear only the customer session keys so admin sessions stay intact
    request.session.pop('customer_id', None)
    request.session.pop('customer_name', None)
    request.session.pop('customer_email', None)
    return redirect("/customerlogin/")

# ----------------- CUSTOMER REGISTRATION -----------------
def customerregister(request):
    if 'customer_id' in request.session:
        return redirect("/shop/")
    return render(request, "customerregister.html")

def savecustomerregister(request):
    if request.method == "POST":
        cname = request.POST.get('cname')
        cemail = request.POST.get('cemail')
        cpassword = request.POST.get('cpassword')
        cphone = request.POST.get('cphone')

        cursor = connections['default'].cursor()

        # Check if email is already registered
        cursor.execute("SELECT customer_id FROM customers WHERE customer_email = %s", [cemail])
        existing_cust = cursor.fetchone()

        if existing_cust:
            return render(request, "customerregister.html", {'error': 'Email is already registered! Please log in.'})

        # Insert new registered customer
        cursor.execute(
            "INSERT INTO customers (customer_name, customer_email, customer_password, customer_phone) VALUES (%s, %s, %s, %s)",
            [cname, cemail, cpassword, cphone]
        )

        # Retrieve the newly inserted customer record to auto-login
        cursor.execute("SELECT customer_id, customer_name, customer_email FROM customers WHERE customer_email = %s", [cemail])
        new_cust = cursor.fetchone()

        request.session['customer_id'] = new_cust[0]
        request.session['customer_name'] = new_cust[1]
        request.session['customer_email'] = new_cust[2]

        return redirect("/shop/")

    return redirect("/customerregister/")

# ----------------- BARCODE SCANNING & BILLING -----------------

def billing(request):
    """Shows the scanning counter screen with current cart items and total."""
    customer_id = request.session.get('customer_id', 1)
    cursor = connections['default'].cursor()

    # Get all scanned items for this customer
    cursor.execute(
        "SELECT cart_id, product_barcode, product_name, product_price FROM cart WHERE customer_id = %s",
        [customer_id]
    )
    items = cursor.fetchall()

    # Calculate grand total
    grand_total = sum(item[3] for item in items) if items else 0.00

    error = request.GET.get('error')
    return render(request, "billing.html", {'items': items, 'grand_total': grand_total, 'error': error})


def scan_barcode(request):
    """Receives scanned barcode, fetches item from products table, inserts into cart."""
    if request.method == "POST":
        barcode = request.POST.get('barcode', '').strip()
        customer_id = request.session.get('customer_id', 1)

        if barcode:
            cursor = connections['default'].cursor()

            # Find product by its barcode
            cursor.execute(
                "SELECT product_name, product_price FROM products WHERE product_barcode = %s",
                [barcode]
            )
            product = cursor.fetchone()

            if product:
                p_name, p_price = product[0], product[1]
                # Insert scanned item into cart
                cursor.execute(
                    "INSERT INTO cart (customer_id, product_barcode, product_name, product_price) VALUES (%s, %s, %s, %s)",
                    [customer_id, barcode, p_name, p_price]
                )
                return redirect("/billing/")
            else:
                return redirect("/billing/?error=Product with this barcode does not exist!")

    return redirect("/billing/")


def delete_cart_item(request, cid):
    """Allows removing an accidental scan from the cart."""
    cursor = connections['default'].cursor()
    cursor.execute("DELETE FROM cart WHERE cart_id = %s", [cid])
    return redirect("/billing/")


def generate_bill(request):
    """Inserts into master_bill, copies lines to sub_bill, and empties cart."""
    customer_id = request.session.get('customer_id', 1)
    cursor = connections['default'].cursor()

    # 1. Fetch current items in cart
    cursor.execute(
        "SELECT product_barcode, product_price FROM cart WHERE customer_id = %s",
        [customer_id]
    )
    cart_items = cursor.fetchall()

    if not cart_items:
        return redirect("/billing/?error=Cart is empty! Scan items before generating bill.")

    # Calculate final total
    total_amount = sum(item[1] for item in cart_items)

    # 2. Insert summary into master_bill
    cursor.execute(
        "INSERT INTO master_bill (customer_id, total_amount) VALUES (%s, %s)",
        [customer_id, total_amount]
    )
    bill_id = cursor.lastrowid

    # 3. Insert each item into sub_bill
    for item in cart_items:
        p_barcode, p_price = item[0], item[1]
        cursor.execute(
            "INSERT INTO sub_bill (bill_id, product_barcode, price) VALUES (%s, %s, %s)",
            [bill_id, p_barcode, p_price]
        )

    # 4. Clear the cart
    cursor.execute("DELETE FROM cart WHERE customer_id = %s", [customer_id])

    # 5. Redirect to print the generated invoice
    return redirect(f"/view_bill/{bill_id}/")


def view_bill(request, bid):
    """Fetches bill details from master_bill and sub_bill for printable receipt."""
    cursor = connections['default'].cursor()

    # Get master bill info
    cursor.execute("SELECT bill_id, customer_id, bill_date, total_amount FROM master_bill WHERE bill_id = %s", [bid])
    bill = cursor.fetchone()

    # Get sub bill line items joined with product name
    cursor.execute("""
        SELECT s.product_barcode, p.product_name, s.price 
        FROM sub_bill s 
        LEFT JOIN products p ON s.product_barcode = p.product_barcode 
        WHERE s.bill_id = %s
    """, [bid])
    items = cursor.fetchall()

    return render(request, "bill_invoice.html", {'bill': bill, 'items': items})