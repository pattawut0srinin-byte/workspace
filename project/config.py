import struct

# Header Format (16 Bytes) & Record Format (64 Bytes)
HEADER_FORMAT, TX_RECORD_FORMAT = "<4sIII", "<BI10sBBfI37s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
TX_RECORD_SIZE = struct.calcsize(TX_RECORD_FORMAT)

DATA_FILE, REPORT_FILE = "transactions.bin", "finance_report.txt"

CATEGORIES = {
    1: "เงินเดือน/รายได้",
    2: "อาหาร/เครื่องดื่ม",
    3: "เดินทาง/น้ำมัน",
    4: "สาธารณูปโภค/ค่าบ้าน",
    5: "ช้อปปิ้ง/บันเทิง",
    99: "อื่นๆ",
}