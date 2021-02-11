from django.shortcuts import render
from django.db.models import Count
from taxManagement.models import Submission, InvoiceHeader



def home_page(request):
    total_invoice_count = InvoiceHeader.objects.all().count()
    total_submited_invoice = Submission.objects.values('invoice').annotate(total=Count('invoice'))
    total_submited_invoice_count = 0 
    
    for invoice in total_submited_invoice:
        total_submited_invoice_count += invoice['total']
    total_not_submited_invoice_count = total_invoice_count-total_submited_invoice_count
    dashboard_context = {
        "total_invoice_count":total_invoice_count,
        "total_submited_invoice_count":total_submited_invoice_count,
        "total_not_submited_invoice_count":total_not_submited_invoice_count
    }
    return render(request, 'index.html', dashboard_context)
