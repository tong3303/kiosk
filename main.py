import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import db_utils

# 세트 할인 금액
SET_DISCOUNT = 1000  # 세트 주문 시 고정 할인

class KioskGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("롯데리아 키오스크")
        self.geometry("900x600")
        self.configure(bg='#f2f2f2')
        db_utils.init_db()
        self.cart = []
        self.create_widgets()


    def create_widgets(self):
        # 카테고리 프레임
        cf = tk.Frame(self, bg='#fff', bd=2, relief='groove')
        cf.place(x=10, y=10, width=200, height=580)
        ttk.Label(cf, text="카테고리").pack(pady=10)
        for cat in db_utils.MENU:
            btn = ttk.Button(cf, text=cat, width=18,
                             command=lambda c=cat: self.show_items(c))
            btn.pack(pady=5)


        # 아이템 프레임
        itf = tk.Frame(self, bg='#fff', bd=2, relief='groove')
        itf.place(x=220, y=10, width=420, height=580)
        self.ilabel = ttk.Label(itf, text="메뉴를 선택하세요")
        self.ilabel.pack(pady=10)
        self.items_box = tk.Listbox(
            itf, font=('Arial', 12), bg='#f9f9f9', bd=0,
            selectbackground='#FFCC00'
        )
        self.items_box.pack(padx=10, fill='both', expand=True)
        ttk.Button(itf, text="추가", command=self.add_item).pack(pady=10)


        # 장바구니 프레임
        cf2 = tk.Frame(self, bg='#fff', bd=2, relief='groove')
        cf2.place(x=650, y=10, width=240, height=580)
        ttk.Label(cf2, text="장바구니").pack(pady=10)
        self.cart_box = tk.Listbox(
            cf2, font=('Arial', 12), bg='#FFF4E6', bd=0,
            selectbackground='#FFE599'
        )
        self.cart_box.pack(padx=10, fill='both', expand=True)
        self.del_btn = ttk.Button(
            cf2, text="삭제", command=self.delete_item,
            state=tk.DISABLED
        )
        self.del_btn.pack(pady=5)
        self.total_label = ttk.Label(cf2, text="합계: 0원")
        self.total_label.pack(pady=10)
        ttk.Button(cf2, text="결제", command=self.checkout).pack(pady=5)
        ttk.Button(
            cf2, text="주문 내역 조회",
            command=self.open_order_history
        ).pack(pady=5)


    def show_items(self, category):
        self.current_category = category
        self.ilabel.config(text=f"{category} 메뉴")
        self.items_box.delete(0, tk.END)
        for itm in db_utils.MENU[category]:
            self.items_box.insert(
                tk.END,
                f"{itm['name']} - {itm['price']}원"
            )


    def add_item(self):
        sel = self.items_box.curselection()
        if not sel:
            messagebox.showwarning("경고", "메뉴를 선택하세요")
            return
        itm = db_utils.MENU[self.current_category][sel[0]]
        # 버거는 단품/세트 선택
        if self.current_category == '버거':
            is_set = messagebox.askyesno(
                "버거 옵션", "세트로 주문하시겠습니까?"
            )
            if is_set:
                self.open_set_popup(itm)
                return
        # 단품 또는 비-버거 메뉴
        qty = simpledialog.askinteger(
            "수량 입력", f"{itm['name']} 수량:", minvalue=1
        )
        if qty:
            self.cart.append({
                'name': itm['name'],
                'price': itm['price'],
                'qty': qty
            })
            self.update_cart()
            

    def open_set_popup(self, burger):
        popup = tk.Toplevel(self)
        popup.title("세트 구성 선택")
        popup.geometry("400x450")
        ttk.Label(popup, text=f"{burger['name']} 세트 구성", font=('Helvetica',14)).pack(pady=10)
        
        
        # 사이드 선택
        ttk.Label(popup, text="사이드 선택").pack(pady=(10,0))
        side_box = tk.Listbox(popup, height=5, exportselection=False)
        for s in db_utils.MENU['사이드']:
            side_box.insert(tk.END, f"{s['name']} - {s['price']}원")
        side_box.pack(fill='x', padx=20, pady=5)
        
        
        # 음료 선택
        ttk.Label(popup, text="음료 선택").pack(pady=(10,0))
        drink_box = tk.Listbox(popup, height=5, exportselection=False)
        for d in db_utils.MENU['음료']:
            drink_box.insert(tk.END, f"{d['name']} - {d['price']}원")
        drink_box.pack(fill='x', padx=20, pady=5)
        def add_set():
            side_sel = side_box.curselection()
            drink_sel = drink_box.curselection()
            if not side_sel or not drink_sel:
                messagebox.showwarning("경고", "사이드와 음료를 각각 선택하세요.")
                return
            s = db_utils.MENU['사이드'][side_sel[0]]
            d = db_utils.MENU['음료'][drink_sel[0]]
            price = burger['price'] + s['price'] + d['price'] - SET_DISCOUNT
            name = f"{burger['name']} 세트({s['name']}, {d['name']})"
            self.cart.append({'name': name, 'price': price, 'qty': 1})
            self.update_cart()
            popup.destroy()
        ttk.Button(popup, text="세트 추가", command=add_set).pack(pady=20)


    def delete_item(self):
        sel = self.cart_box.curselection()
        if not sel:
            return
        self.cart.pop(sel[0])
        self.update_cart()


    def update_cart(self):
        self.cart_box.delete(0, tk.END)
        total = 0
        for e in self.cart:
            line = f"{e['name']} x{e['qty']} - {e['price']*e['qty']}원"
            self.cart_box.insert(tk.END, line)
            total += e['price'] * e['qty']
        self.total_label.config(text=f"합계: {total}원")
        state = tk.NORMAL if self.cart else tk.DISABLED
        self.del_btn.config(state=state)


    def open_order_history(self):
        orders = db_utils.get_all_orders()
        popup = tk.Toplevel(self)
        popup.title("주문 내역")
        popup.geometry("600x400")
        cols = ("주문시간", "메뉴명", "수량", "단가", "합계")
        tree = ttk.Treeview(popup, columns=cols, show='headings')
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor='center')
        tree.pack(fill='both', expand=True)
        for row in orders:
            tree.insert('', tk.END, values=row)


    def checkout(self):
        if not self.cart:
            messagebox.showinfo("정보", "장바구니가 비어 있습니다.")
            return
        db_utils.save_order(self.cart)
        messagebox.showinfo(
            "완료", "결제가 완료되었습니다.\n감사합니다!"
        )
        self.destroy()

if __name__ == '__main__':
    app = KioskGUI()
    app.mainloop()
