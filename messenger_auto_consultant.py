import sqlite3, sys, os, uuid, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("💬 MESSENGER AUTO-CONSULTANT & NICHE ADVISOR ENGINE (V29.0)")
print("=================================================================")

# Industry Consult Scripts Matrix
INDUSTRY_CONSULT_SCRIPTS = {
    'fashion_accessories': {
        'industry_name': '🎒 Balo, Túi Xách & Phụ Kiện',
        'assigned_agent': 'Mai Anh (VIP Closing Agent)',
        'greeting': 'Chào {customer_name} ạ! Em thấy anh/chị đang quan tâm đến mẫu Balo Laptop Oxford chống nước bên em đúng không ạ? 🥰',
        'pitch': 'Mẫu balo này chất liệu vải Oxford 900D cao cấp chống nước 100%, có ngăn chống sốc riêng cho laptop 15.6 inch rất êm ái ạ.',
        'offer': 'Hôm nay bên em đang có voucher giảm 50% chỉ còn 249.000đ (giá gốc 500.000đ) + Miễn phí vận chuyển toàn quốc ạ!',
        'aff_slug': 'deal_grp_balo_01'
    },
    'sneaker_streetwear': {
        'industry_name': '👟 Giày Sneaker & Thời Trang GenZ',
        'assigned_agent': 'Khánh Linh (VIP Closing Agent)',
        'greeting': 'Hế lô {customer_name} nha! Bạn đang tìm mẫu Sneaker Auth đi học đi chơi chuẩn ngầu đúng không nè? 👟',
        'pitch': 'Đôi này đế cao su đúc nguyên khối đi cực êm chân, phối đồ kiểu Streetstyle hay Casual đều bao ngầu luôn nhé!',
        'offer': 'Đang có đợt Flash Sale giảm 40% chỉ còn 489.000đ cho 20 bạn đầu tiên đặt qua link hôm nay nè!',
        'aff_slug': 'deal_grp_snk_01'
    },
    'home_appliances': {
        'industry_name': '🏠 Đồ Gia Dụng & Thiết Bị Thông Minh',
        'assigned_agent': 'Quỳnh Trang (Gia Dụng Specialist)',
        'greeting': 'Em chào chị {customer_name} ạ! Chị đang cần tư vấn mẫu Nồi Chiên Không Dầu dung tích lớn cho gia đình đúng không ạ? 🍲',
        'pitch': 'Dòng nồi chiên này dung tích 8L công nghệ nướng đối lưu 360 độ giúp thức ăn giòn rụm mà không cần dầu mỡ, rất tốt cho sức khỏe cả nhà ạ.',
        'offer': 'Đang có chương trình trợ giá gia dụng giảm ngay 600.000đ kèm quà tặng bộ phụ kiện làm bánh trị giá 200k ạ!',
        'aff_slug': 'deal_grp_home_01'
    },
    'beauty_cosmetics': {
        'industry_name': '💄 Mỹ Phẩm & Skincare Làm Đẹp VIP',
        'assigned_agent': 'Nguyễn Hồng Nhung (Skincare Specialist)',
        'greeting': 'Dạ em chào chị {customer_name} xinh đẹp ạ! Chị đang muốn tư vấn Serum Dưỡng Trắng Mờ Thâm chuẩn y khoa đúng không chị? ✨',
        'pitch': 'Tinh chất này chứa 10% Niacinamide + Arbutin thẩm thấu cực nhanh, giúp da căng bóng rạng rỡ chỉ sau 14 ngày sử dụng ạ.',
        'offer': 'Hôm nay hãng đang áp mã mua 1 tặng 1 tặng kèm kem chống nắng du lịch cao cấp đó chị ơi!',
        'aff_slug': 'deal_grp_beauty_01'
    }
}

# Sample Customer Leads Queue
SAMPLE_CUSTOMER_LEADS = [
    {'name': 'Nguyễn Văn Hải', 'industry': 'fashion_accessories'},
    {'name': 'Phạm Thùy Linh', 'industry': 'beauty_cosmetics'},
    {'name': 'Trần Hoàng Nam', 'industry': 'sneaker_streetwear'},
    {'name': 'Lê Minh Thu', 'industry': 'home_appliances'}
]

def auto_consult_and_send_messages():
    print("\n[Messenger Auto-Consultant] Kích hoạt tự động nhắn tin & tư vấn sản phẩm chuẩn Ngành/Ngách...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Create inbox_conversations table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inbox_conversations (
            id TEXT PRIMARY KEY,
            customer_name TEXT,
            industry TEXT,
            agent_name TEXT,
            message_text TEXT,
            status TEXT DEFAULT 'sent',
            sent_at TEXT
        )
    """)
    
    total_consulted = 0
    now = datetime.now()
    
    for lead in SAMPLE_CUSTOMER_LEADS:
        cname = lead['name']
        ind_key = lead['industry']
        script_info = INDUSTRY_CONSULT_SCRIPTS[ind_key]
        
        agent_name = script_info['assigned_agent']
        greeting = script_info['greeting'].format(customer_name=cname)
        pitch = script_info['pitch']
        offer = script_info['offer']
        slug = script_info['aff_slug']
        
        full_msg = f"{greeting}\n\n👉 {pitch}\n🎁 {offer}\n👉 Xem chi tiết & đặt hàng giữ ưu đãi tại đây chị nha: http://localhost:5000/r/{slug}"
        
        cid = f"conv_{uuid.uuid4().hex[:8]}"
        sent_time = now.isoformat()
        
        cursor.execute("""
            INSERT INTO inbox_conversations (id, customer_name, industry, agent_name, message_text, status, sent_at)
            VALUES (?, ?, ?, ?, ?, 'sent', ?)
        """, (cid, cname, script_info['industry_name'], agent_name, full_msg, sent_time))
        
        total_consulted += 1
        print(f"\n💬 [Messenger Lead #{total_consulted}] Khách hàng: '{cname}' | Ngành: {script_info['industry_name']}")
        print(f"   👤 Nick AI Phụ Trách: {agent_name}")
        print(f"   📲 Nội dung đã tự động gửi tư vấn:\n{full_msg[:120]}...")
        
    conn.commit()
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 MESSENGER ENGINE: ĐÃ TỰ ĐỘNG NHẮN TIN TƯ VẤN THÀNH CÔNG CHO {total_consulted} KHÁCH HÀNG!")
    print("=================================================================")
    
    return {
        'status': 'success',
        'total_consulted': total_consulted
    }

if __name__ == '__main__':
    auto_consult_and_send_messages()
