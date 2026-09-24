from datetime import datetime
import os, struct
from config import CATEGORIES, DATA_FILE, HEADER_FORMAT, HEADER_SIZE, REPORT_FILE, TX_RECORD_FORMAT, TX_RECORD_SIZE

def pack_string(text: str, length: int) -> bytes:
    return text.encode("utf-8")[:length].ljust(length, b"\x00")

def unpack_string(raw_bytes: bytes) -> str:
    return raw_bytes.decode("utf-8", errors="ignore").rstrip("\x00")

def init_binary_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "wb") as f:
            f.write(struct.pack(HEADER_FORMAT, b"FINT", 0, 0, 0))
            f.flush()
            os.fsync(f.fileno())

def get_file_metrics():
    if not os.path.exists(DATA_FILE):
        return 0, 0, 0
    with open(DATA_FILE, "rb") as f:
        header = f.read(HEADER_SIZE)
        if len(header) < HEADER_SIZE:
            return 0, 0, 0
        _, total, active, _ = struct.unpack(HEADER_FORMAT, header)
        return total, active, total - active

def add_transaction(tx_id: int, date_str: str, type_flag: int, category_id: int, amount: float, note: str):
    init_binary_file()
    with open(DATA_FILE, "r+b") as f:
        magic, total, active, free_head = struct.unpack(HEADER_FORMAT, f.read(HEADER_SIZE))
        
        # ตรวจสอบ ID ซ้ำ
        while chunk := f.read(TX_RECORD_SIZE):
            if struct.unpack(TX_RECORD_FORMAT, chunk)[:2] == (1, tx_id):
                return False, "รหัสรายการนี้มีอยู่ในระบบแล้ว!"

        new_rec = struct.pack(TX_RECORD_FORMAT, 1, tx_id, pack_string(date_str, 10), type_flag, category_id, amount, 0, pack_string(note, 37))

        if free_head > 0:
            f.seek(free_head)
            next_free = struct.unpack(TX_RECORD_FORMAT, f.read(TX_RECORD_SIZE))[6]
            f.seek(free_head)
            f.write(new_rec)
            f.seek(0)
            f.write(struct.pack(HEADER_FORMAT, magic, total, active + 1, next_free))
        else:
            f.seek(0, os.SEEK_END)
            f.write(new_rec)
            f.seek(0)
            f.write(struct.pack(HEADER_FORMAT, magic, total + 1, active + 1, free_head))

        f.flush()
        os.fsync(f.fileno())
    return True, "บันทึกรายการสำเร็จ!"

def get_all_transactions():
    if not os.path.exists(DATA_FILE):
        return []
    tx_list = []
    with open(DATA_FILE, "rb") as f:
        f.seek(HEADER_SIZE)
        while chunk := f.read(TX_RECORD_SIZE):
            if len(chunk) < TX_RECORD_SIZE: break
            u = struct.unpack(TX_RECORD_FORMAT, chunk)
            if u[0] == 1:
                tx_list.append({
                    "id": u[1], "date": unpack_string(u[2]),
                    "type": "Income" if u[3] == 1 else "Expense",
                    "type_flag": u[3], "cat_id": u[4],
                    "cat_name": CATEGORIES.get(u[4], "อื่นๆ"),
                    "amount": u[5], "note": unpack_string(u[7])
                })
    return tx_list

def update_transaction(tx_id: int, new_amount: float, new_note: str):
    if not os.path.exists(DATA_FILE): return False, "ไม่พบไฟล์ข้อมูล"
    with open(DATA_FILE, "r+b") as f:
        f.seek(HEADER_SIZE)
        offset = HEADER_SIZE
        while chunk := f.read(TX_RECORD_SIZE):
            if len(chunk) < TX_RECORD_SIZE: break
            u = list(struct.unpack(TX_RECORD_FORMAT, chunk))
            if u[0] == 1 and u[1] == tx_id:
                u[5], u[7] = new_amount, pack_string(new_note, 37)
                f.seek(offset)
                f.write(struct.pack(TX_RECORD_FORMAT, *u))
                f.flush()
                os.fsync(f.fileno())
                return True, "อัปเดตข้อมูลสำเร็จ!"
            offset += TX_RECORD_SIZE
    return False, "ไม่พบรหัสรายการที่ระบุ"

def delete_transaction(tx_id: int):
    if not os.path.exists(DATA_FILE): return False, "ไม่พบไฟล์ข้อมูล"
    with open(DATA_FILE, "r+b") as f:
        magic, total, active, free_head = struct.unpack(HEADER_FORMAT, f.read(HEADER_SIZE))
        offset = HEADER_SIZE
        while chunk := f.read(TX_RECORD_SIZE):
            if len(chunk) < TX_RECORD_SIZE: break
            u = list(struct.unpack(TX_RECORD_FORMAT, chunk))
            if u[0] == 1 and u[1] == tx_id:
                u[0], u[6] = 0, free_head
                f.seek(offset)
                f.write(struct.pack(TX_RECORD_FORMAT, *u))
                f.seek(0)
                f.write(struct.pack(HEADER_FORMAT, magic, total, active - 1, offset))
                f.flush()
                os.fsync(f.fileno())
                return True, "ลบรายการเรียบร้อยแล้ว!"
            offset += TX_RECORD_SIZE
    return False, "ไม่พบรหัสรายการที่ระบุ"

def generate_report():
    init_binary_file()
    tot_recs, act_recs, del_recs = get_file_metrics()
    tx_list = get_all_transactions()

    inc = sum(t["amount"] for t in tx_list if t["type_flag"] == 1)
    exp = sum(t["amount"] for t in tx_list if t["type_flag"] == 2)
    net = inc - exp

    lines = [
        "=" * 66, f"{'INCOME & EXPENSE SYSTEM REPORT (.txt)':^66}", f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 66, "",
        "[1] SYSTEM & FILE METRICS", "-" * 66,
        f"{'File Name':<18} {'Total Recs':<12} {'Active Recs':<12} {'Deleted (Free-List)':<20}", "-" * 66,
        f"{'transactions.bin':<18} {tot_recs:<12} {act_recs:<12} {del_recs:<20}", "-" * 66, "",
        "[2] FINANCIAL SUMMARY (OVERALL)", "-" * 66,
        f"{'Total Income Amount':<32} : {inc:,.2f} THB",
        f"{'Total Expense Amount':<32} : {exp:,.2f} THB", "-" * 66,
        f"{'NET BALANCE':<32} : {'+' if net >= 0 else ''}{net:,.2f} THB", "",
        "[3] RECENT TRANSACTIONS LOG", "-" * 66,
        f"{'Tx ID':<8} | {'Date':<10} | {'Type':<8} | {'Amount (THB)':<14} | {'Note'}", "-" * 66
    ]

    for t in reversed(tx_list[-10:]):
        prefix = "+" if t['type_flag'] == 1 else "-"
        lines.append(f"{t['id']:06d}   | {t['date']:<10} | {t['type']:<8} | {prefix}{t['amount']:,.2f}:<14 | {t['note']}")

    lines.append("=" * 66)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.flush()
        os.fsync(f.fileno())
    return REPORT_FILE