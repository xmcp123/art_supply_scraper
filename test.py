from macpherson import MacPhersonProductList

class dummy:
    def get_results(self):
        return []

d=dummy()
mp = MacPhersonProductList(d)

mp.add_product((
    'http://www.macphersonart.com/cgi-bin/maclive/olc/drill-down3.w?parent=147492&secnav=no&type=subtitle&sponsor=200000&nocache=59605','test'))