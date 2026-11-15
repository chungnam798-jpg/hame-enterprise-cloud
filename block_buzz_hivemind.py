import sqlite3, uuid, sys, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("🐝 BLOCK BUZZ HIVE-MIND AGENT COLLABORATION ENGINE (V29.0)")
print("=================================================================")

def get_hivemind_agent_network():
    """Lấy danh sách trọn bộ 10 AI Agents kèm định danh Cryptographic Role & Trạng thái."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, team_role, status FROM accounts")
    accounts = cursor.fetchall()
    conn.close()
    
    agent_network = []
    for acc in accounts:
        agent_network.append({
            'agent_id': acc[0],
            'agent_name': acc[1],
            'role': acc[2],
            'crypto_identity': f"npub1{acc[0][:8]}buzzhive",
            'status': acc[3],
            'capabilities': ['auto_post', 'ai_comment', 'cross_sell']
        })
        
    return {
        'status': 'success',
        'hive_mind': 'BLOCK_BUZZ_HIVEMIND_V29',
        'active_agent_count': len(agent_network),
        'agents': agent_network
    }

def broadcast_hivemind_event(event_type, payload):
    """Phát sóng tín hiệu phối hợp giữa 10 AI Agents (Hive-Mind Event Bus)."""
    print(f"\n[Buzz Hive-Mind Bus] 📢 Phát sóng sự kiện: {event_type}")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Fetch Seeding Accounts
    cursor.execute("SELECT id, name FROM accounts WHERE team_role = 'team_seeding' AND status = 'active'")
    seeders = cursor.fetchall()
    
    now_str = datetime.now().isoformat()
    triggered_seeders = []
    
    for s in seeders:
        triggered_seeders.append(s[1])
        print(f"   🐝 Agent Seeding '{s[1]}' ({s[0]}) đã nhận tín hiệu và sẵn sàng mồi comment!")
        
    conn.close()
    
    return {
        'status': 'success',
        'event': event_type,
        'payload': payload,
        'responded_seeders': triggered_seeders,
        'timestamp': now_str
    }

if __name__ == '__main__':
    net = get_hivemind_agent_network()
    print(f"✅ Đã kết nối thành công mạng lưới {net['active_agent_count']} AI Agents!")
    res = broadcast_hivemind_event('NEW_DEAL_POSTED', {'post_title': 'Balo Laptop Sale 60%'})
    print(json.dumps(res, ensure_ascii=False, indent=2))
