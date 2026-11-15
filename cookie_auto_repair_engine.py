import sqlite3, sys, os, json

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🛡️ COOKIE AUTO-REPAIR & ACCOUNT MAPPING GUARD ENGINE (V29.0)")
print("=================================================================")

# Full 10 Accounts ID & Name Map
FULL_ACCOUNT_MAP = {
    'acc_18': 'acc_1846ba62',
    'acc_39': 'acc_39b1898f',
    'acc_b5': 'acc_b5bc701c',
    'acc_34': 'acc_34a8389d',
    'acc_6b': 'acc_6be62ca0',
    'acc_4e': 'acc_4ec19419',
    'acc_a2': 'acc_a2c6d4d1',
    'acc_33': 'acc_33d3ff4a',
    'acc_11': 'acc_11cbebc1',
    'acc_a8': 'acc_a829d1f1'
}

def repair_account_mappings_and_failed_posts():
    print("\n[Cookie & Account Guard] Đang kiểm tra & Sửa lỗi Mapped Account IDs + Khôi phục bài đăng thất bại...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Fetch active full account IDs
    cursor.execute("SELECT id, name, status, LENGTH(cookie) FROM accounts WHERE status = 'active'")
    active_accounts = cursor.fetchall()
    print(f"   👥 Số tài khoản đang Active trong Database: {len(active_accounts)}")
    
    if not active_accounts:
        print("   ⚠️ Không tìm thấy tài khoản active.")
        conn.close()
        return {'status': 'error', 'message': 'No active accounts found.'}
        
    full_ids = [acc[0] for acc in active_accounts]
    
    # 2. Map short IDs to full IDs in posts table
    mapped_count = 0
    for short_id, full_id in FULL_ACCOUNT_MAP.items():
        cursor.execute("UPDATE posts SET account_id = ? WHERE account_id = ?", (full_id, short_id))
        mapped_count += cursor.rowcount
        
    print(f"   🔄 Đã chuyển đổi {mapped_count} bài đăng từ ID ngắn sang Full Account ID chính xác.")
    
    # 3. Reset failed posts to pending with round-robin full account assignment
    cursor.execute("SELECT id FROM posts WHERE status = 'failed'")
    failed_posts = cursor.fetchall()
    print(f"   🛠️ Tìm thấy {len(failed_posts)} bài đăng bị lỗi. Đang chuyển về 'pending' & gán lại Nick Active...")
    
    reassigned_count = 0
    for idx, (post_id,) in enumerate(failed_posts):
        assigned_acc = full_ids[idx % len(full_ids)]
        cursor.execute("UPDATE posts SET status = 'pending', account_id = ?, updated_at = datetime('now') WHERE id = ?", (assigned_acc, post_id))
        reassigned_count += 1
        
    # 4. Check for any remaining null account_id
    cursor.execute("SELECT id FROM posts WHERE account_id IS NULL OR account_id = ''")
    null_posts = cursor.fetchall()
    for idx, (post_id,) in enumerate(null_posts):
        assigned_acc = full_ids[idx % len(full_ids)]
        cursor.execute("UPDATE posts SET account_id = ? WHERE id = ?", (assigned_acc, post_id))
        
    conn.commit()
    
    # 5. Fetch updated stats
    cursor.execute("SELECT status, COUNT(*) FROM posts GROUP BY status")
    stats = dict(cursor.fetchall())
    
    conn.close()
    
    print("\n=================================================================")
    print(f"🎉 THÀNH CÔNG: ĐÃ KHÔI PHỤC {reassigned_count} BÀI ĐĂNG LỖI THÀNH PENDING!")
    print(f"📊 Trạng thái Hàng Đợi Mới: {stats}")
    print("=================================================================")
    
    return {
        'status': 'success',
        'reassigned_failed_posts': reassigned_count,
        'mapped_short_ids': mapped_count,
        'queue_stats': stats
    }

if __name__ == '__main__':
    repair_account_mappings_and_failed_posts()
