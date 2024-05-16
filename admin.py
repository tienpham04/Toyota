from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from .models import *

# excel
from io import BytesIO
import pandas as pd

# pdf
from reportlab.pdfgen import canvas
from reportlab. lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab. lib import colors

# pdf function
def download_pdf(self, request, queryset):
    model_name = self.model.__name__
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={model_name}.pdf'

    headers = ["Order ID", "Customer", "Order Date", "Car", "Quantity", "Order Add"]
    data = [headers]

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle('Receipt Buy Car')

    pdf.drawString(40, 750, "Receipt Buy Car")
    row_height = 20  # Adjust as needed
    start_y = 600  # Adjust as needed
    current_y = start_y

    for order in queryset:
        order_details = order.orderdetail_set.all()
        for detail in order_details:
            data_row = [
                str(order.id),
                order.customer.username,
                order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
                detail.car.nameCar,
                str(detail.quantity),
                detail.order_add
            ]
            data.append(data_row)

    table = Table(data)
    table.setStyle(TableStyle(
        [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]
    ))

    canvas_width = 600
    canvas_height = 730
    table.wrapOn(pdf, canvas_width, canvas_height)
    table.drawOn(pdf, 40, canvas_height - len(data) * row_height)

    # Display text after the table
    text_lines = [
        "Chinh sach bao duong",
        "1 Thoi han bao hanh",
        "Che do bao hanh bat dau duoc tinh ngay ke tu thoi diem xe duoc giao cho chu xe dau tien Trong vong 36", 
        "thang hoac 100 000 km tuy thuoc dieu kien nao den truoc Toyota dam bao se sua chua hoac thay the bat",
        "ky phu tung nao cua xe Toyota moi bi hong hoc",
        "Bao hanh ac quy Thoi han bao hanh cho ac quy la 12 thang hoac 20 000 km tuy dieu kien nao den truoc",
        "Bao hanh ac quy hybrid Thoi han bao hanh ac quy hybrid la 36 60 thang hoac 100 000 150 000 km tuy loai",
        "xe tuy dieu kien nao den truoc",
        "Bao hanh lop Bao hanh lop Ðuoc bao hanh theo che do rieng cua nha san xuat lop De biet them chi tiet",
        "xin quy khach vui long tham khao nhung trang web sau Bridgestone Dunlop Michelin",
        "2 Dieu kien bao hanh",
        "Toyota chi dam bao sua chua thay the cac phu tung cua xe Toyota moi bi hong hoc trong dieu kien",
        "Xe hoat dong trong dieu kien binh thuong",
        "Nguyen lieu phu tung khong tot",
        "Loi lap rap",
        "Tru nhung dieu kien ghi trong muc NHUNG GI KHONG DUOC BAO HANH",
        "Chu y Bao hanh van ap dung khi xe duoc chuyen nhuong cho nhung chu xe khac",
        "3 Pham vi ap dung bao hanh",
        "Bao hanh chi ap dung trong pham vi nuoc Cong hoa Xa hoi chu nghia Viet Nam",
        "4 Bao hanh mien phi",
        "Moi sua chua thuoc che do bao hanh phu tung cong lao dong la mien phi",
        "Xin quy khach hang luu y",
        "Chinh sach bao hanh tai Website nay la nhung thong tin co ban nhat ve viec bao hanh xe noi chung",
        "Chinh sach bao hanh co the co su khac nhau giua cac dong xe",
        "Vi vay moi quy khach hang tham khao tai So bao hanh di kem san pham de biet them cac thong tin bao",
        "hanh chi tiet va chinh sach bao hanh dac biet hon cho tung dong xe"
    ]

    for line in text_lines:
        pdf.setFont("Helvetica", 12)
        pdf.drawString(40, current_y, line)
        current_y -= 20  # Adjust as needed for spacing

    pdf.save()
    return response

    download_pdf.short_description = "Download seleted items as PDF."


class CarAdmin(admin.ModelAdmin):
  list_display = ("id", "nameCar", "image", "descriptions", "price", "quantity", "prioritize")
  # excel function
  def generate_excel_file(self, data, file_name):
      excel_file = BytesIO()
      writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
      df = pd.DataFrame.from_dict(data=data)
      df.to_excel(writer, sheet_name='Sheet 1', index=False)
      writer.close()
      excel_file.seek(0)
      response = HttpResponse(excel_file.read(),
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      response['Content-Disposition'] = f"attachment; filename={file_name}"
      return response

  def get_urls(self):
    urls = super().get_urls()
    product_url = [path('product-report/', self.download_product_data), ]
    return product_url + urls

  def download_product_data(self, request):
    all_product_values = Product.objects.all() 
    product_data = {"Id": [], "Name": [], "Price": [], "Quantity": [], "Provider": [] }
    for product in all_product_values:
      product_data['Id'].append(product.id)
      product_data['Name'].append(product.name)
      product_data['Price'].append(product.price)
      product_data['Quantity'].append(product.quantity)
      product_data['Provider'].append(product.provider)

    return self.generate_excel_file(data=product_data, file_name="Product.xlsx")
    
  actions = [generate_excel_file]
  

class CustomerAdmin(admin.ModelAdmin):
  list_display = ("username", "phone", "address", "own_car","prioritize")

class CategoryAdmin(admin.ModelAdmin):
  list_display = ("name",)

class ProductAdmin(admin.ModelAdmin):
  list_display = ("name", "price", "quantity", "provider")


class OderAdmin(admin.ModelAdmin):
  list_display = ('customer', 'order_date',)

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    fields = ['car', 'quantity', 'order_add']
    extra = 1
    

class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order_date')
    inlines = [OrderDetailInline]
    actions = [download_pdf]

admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Order, OrderAdmin)

admin.site.register(ShippingAddress)
admin.site.register(Car,CarAdmin)
admin.site.register(Customer,CustomerAdmin)

