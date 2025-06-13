import sqlite3
from datetime import datetime

DB_NAME = 'orders.db'

# 메뉴 데이터 (공유)
MENU = {
    '버거': [
        {'id': 1, 'name': '불고기버거', 'price': 3500},
        {'id': 2, 'name': '새우버거',   'price': 3000},
        {'id': 3, 'name': '치즈버거',   'price': 3200},
        {'id': 4, 'name': '와퍼주니어', 'price': 4500},
        {'id': 5, 'name': '불고기와퍼', 'price': 5500},
        {'id': 6, 'name': '치킨버거',   'price': 4000},
        {'id': 7, 'name': '몬스터X',    'price': 6000},
        {'id': 8, 'name': '아보카도통살','price': 6500},
        {'id': 9, 'name': '모짜렐라통살','price': 6200},
        {'id':10, 'name': '라이스버거', 'price': 4800},
        {'id':11, 'name': '더블불고기버거','price':7000},
        {'id':12, 'name': '통새우버거', 'price': 5300},
        {'id':13, 'name': '스파이시통다리','price':5800},
        {'id':14, 'name': '포테이토통살','price':6300},
        {'id':15, 'name': '어니언통살버거','price':6100},
    ],
    '사이드': [
        {'id': 1, 'name': '감자튀김',  'price': 1500},
        {'id': 2, 'name': '어니언링',  'price': 1800},
        {'id': 3, 'name': '치즈스틱',  'price': 2000},
        {'id': 4, 'name': '치킨너겟',  'price': 2500},
        {'id': 5, 'name': '샐러드',    'price': 3000},
        {'id': 6, 'name': '나초',      'price': 2200},
        {'id': 7, 'name': '치즈볼',    'price': 2300},
        {'id': 8, 'name': '콜슬로',    'price': 1700},
        {'id': 9, 'name': '베이컨랩',  'price': 2600},
        {'id':10, 'name': '스파이시윙','price': 2800},
    ],
    '음료': [
        {'id': 1, 'name': '콜라',       'price': 1200},
        {'id': 2, 'name': '사이다',     'price': 1200},
        {'id': 3, 'name': '환타',       'price': 1300},
        {'id': 4, 'name': '아메리카노', 'price': 2000},
        {'id': 5, 'name': '오렌지주스', 'price': 1800},
        {'id': 6, 'name': '토마토주스', 'price': 1900},
    ],
}


def init_db():
    """DB와 orders 테이블 초기화"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_time TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price INTEGER NOT NULL,
            total_price INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_order(cart_items):
    """장바구니(cart_items)의 주문을 DB에 저장"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in cart_items:
        total = item['price'] * item.get('qty', 1)
        cur.execute(
            'INSERT INTO orders (order_time, item_name, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)',
            (order_time, item['name'], item.get('qty', 1), item['price'], total)
        )
    conn.commit()
    conn.close()


def get_all_orders():
    """전체 주문 내역을 조회하여 반환"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        'SELECT order_time, item_name, quantity, unit_price, total_price FROM orders'
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_orders_by_date(date_str):
    """특정 날짜(date_str, YYYY-MM-DD)에 주문 내역 조회"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        'SELECT order_time, item_name, quantity, unit_price, total_price'
        ' FROM orders WHERE order_time LIKE ?',
        (f"{date_str}%",)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_order(order_id):
    """주문 ID로 특정 주문 삭제"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()


def clear_orders():
    """orders 테이블 전체 삭제"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM orders')
    conn.commit()
    conn.close()


def get_sales_summary_by_date(date_str):
    """특정 날짜 매출 합계 반환"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        'SELECT SUM(total_price) FROM orders WHERE order_time LIKE ?',
        (f"{date_str}%",)
    )
    total = cur.fetchone()[0] or 0
    conn.close()
    return total
