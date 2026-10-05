from django.contrib import admin
from django.urls import path

import Myapp.views

urlpatterns = [
    path("",Myapp.views.home),
    path("about/",Myapp.views.about),
    path("ins/",Myapp.views.ins),
    path("shop/",Myapp.views.shop),

    path("dashboard/",Myapp.views.dashboard),
    path("addproduct/",Myapp.views.addproduct),
    path("insproduct/",Myapp.views.insproduct),
    path("listproducts/",Myapp.views.listproducts),
    path("deleteproduct/<int:pid>",Myapp.views.deleteproduct),

    path("addcustomer/", Myapp.views.addcustomer),
    path("inscustomer/", Myapp.views.inscustomer),
    path("listcustomer/", Myapp.views.listcustomer),

    path("customerlogin/", Myapp.views.customerlogin),
    path("checkcustomerlogin/", Myapp.views.checkcustomerlogin),
    path("customerlogout/", Myapp.views.customerlogout),

    path("customerregister/", Myapp.views.customerregister),
    path("savecustomerregister/", Myapp.views.savecustomerregister),

    path("billing/", Myapp.views.billing),
    path("scan_barcode/", Myapp.views.scan_barcode),
    path("delete_cart_item/<int:cid>/", Myapp.views.delete_cart_item),
    path("generate_bill/", Myapp.views.generate_bill),
    path("view_bill/<int:bid>/", Myapp.views.view_bill),
]