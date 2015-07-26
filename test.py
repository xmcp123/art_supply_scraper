from macpherson import MacPhersonProductList

class dummy:
    def get_results(self):
        return []

d=dummy()
mp = MacPhersonProductList(d)

mp.add_product((
    'http://www.macphersonart.com/cgi-bin/maclive/olc/drill-down3.w?asstMode=yes&vendor=ADV00068&brand=ADB00077&product=PO1CV160&sponsor=200000&nocache=61469','test'))