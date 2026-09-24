from datetime import datetime
import os
from config import CATEGORIES, DATA_FILE, TX_RECORD_SIZE
from database import add_transaction, delete_transaction, get_all_transactions, get_file_metrics, update_transaction
class Style:
    BOLD = '\033[1m'
    RESET = '\033[0m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BG_GREEN = '\033[42m'
    BG_WHITE = '\033[47m'

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title=""):
    clear_screen()
    print("=" * 66)
    print(f"|{Style.BOLD}{Style.BG_GREEN}                   INCOME & EXPENSE SYSTEM                      {Style.RESET}|")
    print("=" * 66)
    if title:
        print("-" * 66)
        print(f" {Style.BOLD}{Style.GREEN}<< {title} >>{Style.RESET}\n" + "-" * 66)

def ui_add_transaction():
    print_header("ADD TRANSACTION (บันทึกรายรับ-รายจ่าย)")
    try:
        print("=" * 66)
        tx_id = int(input("ป้อนรหัสรายการ (ID ตัวเลข): "))
        date_str = input("ป้อนวันที่ (YYYY-MM-DD) [เว้นว่างไว้ใช้ใช้วันนี้]: ").strip() or datetime.now().strftime("%Y-%m-%d")

        print("\nเลือกประเภทธุรกรรม:\n 1) รายรับ (Income)\n 2) รายจ่าย (Expense)")
        type_flag = int(input("เลือก (1-2): "))
        if type_flag not in (1, 2):
            print(f"\n[{Style.RED}ERROR{Style.RESET}] ประเภทธุรกรรมไม่ถูกต้อง!")
            return input("\nกด Enter เพื่อลองใหม่...")

        print("\nหมวดหมู่รายการ:")
        for k, v in CATEGORIES.items(): print(f" {k}) {v}")
        cat_id = int(input("เลือกหมวดหมู่ (ตัวเลข): "))

        amount = float(input("\nป้อนจำนวนเงิน (บาท): "))
        if amount <= 0:
            print(f"\n[{Style.RED}ERROR{Style.RESET}] จำนวนเงินต้องมากกว่า 0")
            return input("\nกด Enter เพื่อลองใหม่...")

        success, msg = add_transaction(tx_id, date_str, type_flag, cat_id, amount, input("บันทึกช่วยจำ (Note): ").strip())
        status_text = f"{Style.GREEN}SUCCESS{Style.RESET}" if success else f"{Style.RED}ERROR{Style.RESET}"
        print(f"\n[{status_text}] {msg}")
    except ValueError:
        print(f"\n[{Style.RED}ERROR{Style.RESET}] รูปแบบข้อมูลตัวเลขไม่ถูกต้อง!")
    input("\nกด Enter เพื่อกลับเมนูหลัก...")

def ui_update_transaction():
    print_header("UPDATE TRANSACTION (แก้ไขรายการ)")
    try:
        tx_id = int(input("ป้อนรหัสรายการที่ต้องการแก้ไข: "))
        amount = float(input("ป้อนจำนวนเงินใหม่ (บาท): "))
        note = input("ป้อนบันทึกช่วยจำใหม่: ").strip()
        success, msg = update_transaction(tx_id, amount, note)
        status_text = f"{Style.GREEN}SUCCESS{Style.RESET}" if success else f"{Style.RED}ERROR{Style.RESET}"
        print(f"\n[{status_text}] {msg}")
    except ValueError:
        print(f"\n[{Style.RED}ERROR{Style.RESET}] ป้อนข้อมูลไม่ถูกต้อง!")
    input("\nกด Enter เพื่อกลับเมนูหลัก...")

def ui_delete_transaction():
    print_header("DELETE TRANSACTION (ลบรายการ)")
    try:
        tx_id = int(input("ป้อนรหัสรายการที่ต้องการลบ: "))
        if input(f"ยืนยันการลบรายการ ID {tx_id}? (y/n): ").strip().lower() == "y":
            success, msg = delete_transaction(tx_id)
            status_text = f"{Style.GREEN}SUCCESS{Style.RESET}" if success else f"{Style.RED}ERROR{Style.RESET}"
            print(f"\n[{status_text}] {msg}")
        else:
            print("\nยกเลิกการลบรายการ")
    except ValueError:
        print(f"\n[{Style.RED}ERROR{Style.RESET}] รหัสรายการต้องเป็นตัวเลข!")
    input("\nกด Enter เพื่อกลับเมนูหลัก")

def ui_view_menu():
    while True:
        print_header("VIEW TRANSACTIONS (ดูรายการ/สถิติการเงิน)")
        print("1) ดูรายการทั้งหมด\n2) ค้นหาจาก ID\n3) กรองเฉพาะ รายรับ/รายจ่าย\n4) สถิติไฟล์\n0) ย้อนกลับ\n" + "-" * 66)
        choice = input("เลือกเมนูย่อย (0-4): ").strip()
        tx_list = get_all_transactions()

        if choice == "1":
            print_header("TRANSACTIONS LIST")
            print(f"{'ID':<6} | {'Date':<10} | {'Type':<8} | {'Category':<15} | {'Amount (THB)':<12} | Note\n" + "-" * 66)
            for t in tx_list:
                sign = '+' if t['type_flag'] == 1 else '-'
                amt_num = f"{sign}{t['amount']:,.2f}"
                color = Style.GREEN if t['type_flag'] == 1 else Style.RED
                amt_str = f"{color}{amt_num:<12}{Style.RESET}"
                print(f"{t['id']:<6} | {t['date']:<10} | {t['type']:<8} | {t['cat_name']:<15}   | {amt_str:<12} | {t['note']}\n" + "-" * 66)
            input("\nกด Enter เพื่อตกลง...")

        elif choice == "2":
            try:
                target_id = int(input("\nป้อนรหัสรายการที่ต้องการค้นหา: "))
                if f := next((t for t in tx_list if t["id"] == target_id), None):
                    sign = '+' if f['type_flag'] == 1 else '-'
                    amt_num = f"{sign}{f['amount']:,.2f}"
                    color = Style.GREEN if f['type_flag'] == 1 else Style.RED
                    amt_str = f"{color}{amt_num:<12}{Style.RESET}"
                    print(f"{'ID':<6} | {'Date':<10} | {'Type':<8} | {'Category':<15} | {'Amount (THB)':<12} |\n"
                          f"{f['id']:<6} | {f['date']:<10} | {f['type']:<8} | {f['cat_name']:<15}   | {amt_str:<12} |\nบันทึกช่วยจำ: {f['note']}")
                else:
                    print(f"\n[{Style.RED}!{Style.RESET}] ไม่พบรายการรหัสนี้")
            except ValueError:
                print(f"\n[{Style.RED}!{Style.RESET}] รหัสต้องเป็นตัวเลข")
            input("\nกด Enter เพื่อตกลง...")

        elif choice == "3":
            t_choice = input("\nเลือกรองรับรายการ:\n 1) เฉพาะรายรับ (Income)\n 2) เฉพาะรายจ่าย (Expense)\nเลือก (1-2): ").strip()
            if t_choice in ("1", "2"):
                filtered = [t for t in tx_list if t["type_flag"] == int(t_choice)]
                print(f"\nรายการที่กรองได้ ({len(filtered)} รายการ):\n" + "-" * 66)
                for t in filtered:
                    sign = '+' if t['type_flag'] == 1 else '-'
                    amt_num = f"{sign}{t['amount']:,.2f}"
                    color = Style.GREEN if t['type_flag'] == 1 else Style.RED
                    amt_str = f"{color}{amt_num}{Style.RESET}"
                    print(f"ID: {t['id']} | {t['date']} | {amt_str} THB | Note: {t['note']}\n" + "-" * 66)
            else:
                print(f"\n[{Style.RED}!{Style.RESET}] เลือกตัวเลือกไม่ถูกต้อง")
            input("\nกด Enter เพื่อตกลง...")

        elif choice == "4":
            tot, act, free = get_file_metrics()
            print_header("FILE & BINARY STATISTICS")
            print(f"ชื่อไฟล์ไบนารี              : {DATA_FILE}\nขนาดต่อระเบียน (Record Size) : {TX_RECORD_SIZE} Bytes\n"
                  f"จำนวน Record ทั้งหมดในดิสก์   : {tot}\nจำนวน Record ที่ใช้งาน (Active): {act}\nจำนวน Record ที่ถูกลบ (Free-List): {free}")
            input("\nกด Enter เพื่อตกลง...")

        elif choice == "0":
            break