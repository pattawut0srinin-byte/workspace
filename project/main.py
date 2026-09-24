import os, sys
from database import generate_report, init_binary_file
from ui import print_header, ui_add_transaction, ui_delete_transaction, ui_update_transaction, ui_view_menu, Style

def main_menu():
    init_binary_file()
    actions = {
        "1": ui_add_transaction,
        "2": ui_update_transaction,
        "3": ui_delete_transaction,
        "4": ui_view_menu,
    }

    while True:
        print_header("MAIN MENU (เมนูหลัก)")
        print("=" * 66)
        print("(1) [Add]  (บันทึกรายรับ-รายจ่าย)\n(2) [Update]  (แก้ไขข้อมูลรายการ)\n(3) [Delete]  (ลบรายการ)\n"
              "(4) [View]  (ดูรายการ)\n(5) [Generate Report] (.txt)\n(0) [Exit]  (ออกจากโปรแกรม)")
        print("=" * 66)
        choice = input("เลือกทำรายการ (0-5): ").strip()
        
        if choice in actions:
            actions[choice]()
        elif choice == "5":
            rep = generate_report()
            print(f"\n{Style.GREEN}SUCCESS{Style.RESET} สร้างไฟล์รายงานสรุปผลการเงินสำเร็จที่:\n{os.path.abspath(rep)}")
            input("\nกด Enter เพื่อกลับเมนูหลัก...")
        elif choice == "0":
            rep = generate_report()
            print(f"\n[SYSTEM] ปิดระบบอย่างปลอดภัย บันทึกไฟล์ไบนารี และสร้างรายงานสรุปเรียบร้อยแล้ว!\n[REPORT] {os.path.abspath(rep)}")
            sys.exit(0)
        else:
            print(f"\n{Style.RED}ERROR{Style.RESET} ตัวเลือกไม่ถูกต้อง กรุณาเลือก 0-5")
            input("กด Enter เพื่อลองใหม่...")

if __name__ == "__main__":
    main_menu()