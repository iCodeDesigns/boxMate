from django.db.models import Sum, Q


class InoviceTaxLineCalculator:
    def __init__(self, invoice_line):
        # total of amounts per invoice line
        self.invoice_line = invoice_line
        self.total_non_taxable_fees = 0
        self.t3 = 0
        self.t6 = 0
        self.t2 = 0
        self.t1 = 0
        self.t4 = 0

    def calculate_all_taxes_amount(self):
        same_tax_equations = ["T5", "T7", "T8", "T9", "T10", "T11", "T12", "T13", "T14", "T15", "T16", "T17",
                              "T18", "T19", "T20"]
        tax_lines_category1 = self.invoice_line.tax_lines.filter(taxType__in=same_tax_equations)

        for tax_line in tax_lines_category1:
            tax_line.amount = tax_line.rate * self.invoice_line.netTotal /100
            tax_line.save()

        tax_line_per_t3 = self.invoice_line.tax_lines.filter(taxType="T3")
        if len(tax_line_per_t3) == 0:
            self.t3 = 0
        else:
            self.t3 = tax_line_per_t3[0].amount

        tax_lines_per_t2 = self.invoice_line.tax_lines.filter(taxType="T2")
        net_total = self.invoice_line.netTotal
        category1 = ["T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
        total_tax_fees = self.invoice_line.tax_lines.filter(taxType__in=category1).values("taxType").aggregate(
            totalTaxableFees=Sum("amount"))['totalTaxableFees']
        if total_tax_fees is None:
            total_tax_fees = 0
        self.invoice_line.totalTaxableFees = total_tax_fees
        self.invoice_line.save()
        valueDifference = self.invoice_line.valueDifference
        for tax_line in tax_lines_per_t2:
            rate = (tax_line.rate / 100)
            tax_line.amount = (net_total + total_tax_fees +
                               valueDifference + self.t3) * rate
            self.t2 += tax_line.amount
            tax_line.save()

        tax_lines_per_t1 = self.invoice_line.tax_lines.filter(taxType="T1")
        for tax_line in tax_lines_per_t1:
            tax_line.amount = (
                                      self.invoice_line.totalTaxableFees + self.invoice_line.valueDifference + self.invoice_line.netTotal +
                                      self.t2 + self.t3) * (tax_line.rate / 100)
            tax_line.save()
            self.t1 += tax_line.amount

        tax_lines_per_t4 = self.invoice_line.tax_lines.filter(taxType="T4")
        for tax_line in tax_lines_per_t4:
            tax_line.amount = (tax_line.rate / 100) * \
                              (self.invoice_line.netTotal - self.invoice_line.itemsDiscount)
            tax_line.save()
            self.t4 += tax_line.amount
        category2 = ["T13", "T14", "T15", "T16", "T17","T18", "T19", "T20"]
        self.total_non_taxable_fees = \
            self.invoice_line.tax_lines.filter(taxType__in=category2).values(
                "taxType").aggregate(
                total_non_taxable_fees=Sum("amount"))['total_non_taxable_fees']
        if self.total_non_taxable_fees is None:
            self.total_non_taxable_fees = 0
