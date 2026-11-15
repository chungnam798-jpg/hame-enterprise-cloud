import sqlite3, sys, os, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

print("=================================================================")
print("📐 LIKEC4 ARCHITECTURE-AS-CODE & C4 VISUALIZER (V29.0 ENGINE)")
print("=================================================================")

ARCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public_architecture')
os.makedirs(ARCH_DIR, exist_ok=True)

def generate_likec4_architecture():
    print("\n[LikeC4 Engine] Đang biên dịch đặc tả kiến trúc LikeC4 DSL & Dựng Sơ Đồ C4 Tương Tác...")
    
    # Declarative C4 DSL Model representation
    c4_model = {
        'system_name': 'HAME Enterprise Suite v29.0 (Autonomous AI Matrix)',
        'version': 'v29.0',
        'tiers': [
            {
                'name': '1. Presentation Tier (Giao diện người dùng & Di động)',
                'components': [
                    {'id': 'pwa_mobile', 'name': 'PWA Mobile App Client', 'type': 'Mobile PWA', 'desc': 'Giao diện điều khiển 60fps trên iPhone/Android'},
                    {'id': 'web_dashboard', 'name': 'Web Admin Dashboard', 'type': 'Flask Web UI', 'desc': 'Bảng điều khiển trung tâm http://localhost:5000'},
                    {'id': 'tele_bot', 'name': 'Telegram Bot Client', 'type': 'Telegram Bot', 'desc': 'Điều hành chụp màn hình & xem doanh thu từ xa'}
                ]
            },
            {
                'name': '2. Autonomous AI Agent Squad Tier (Ma trận 10 Nicks Facebook)',
                'components': [
                    {'id': 'team_vip', 'name': 'VIP Profile Agents (2 Nicks)', 'type': 'Closing Agent', 'desc': 'Phạm Khánh Linh & Mai Anh - Trực Inbox 24/7'},
                    {'id': 'team_poster', 'name': 'Flash Sale Poster Agents (5 Nicks)', 'type': 'Posting Agent', 'desc': 'Thanh Hằng, Ngọc Trinh, Hoàng Yến, Minh Thư, Quỳnh Trang - Cào deal & rải bài'},
                    {'id': 'team_seeding', 'name': 'Seeding Agents (3 Nicks)', 'type': 'Engagement Agent', 'desc': 'Hà Vi, Linh Nhi, Thu Hà - Mồi comment & tăng tương tác'}
                ]
            },
            {
                'name': '3. Core Intelligence Engines Tier (8 Phân hệ AI đỉnh cao)',
                'components': [
                    {'id': 'eng_codebuff', 'name': 'Codebuff Multi-Agent', 'desc': 'Phối hợp 4 Sub-Agents Extractor, Planner, Editor, Reviewer'},
                    {'id': 'eng_superpowers', 'name': 'Obra Superpowers QA', 'desc': 'Kiểm soát 4 tầng kỷ luật & VACUUM CSDL'},
                    {'id': 'eng_worldmonitor', 'name': 'World Monitor Trend Radar', 'desc': 'Quét 500+ nguồn tin tức & xu hướng tiêu dùng'},
                    {'id': 'eng_instatic', 'name': 'Instatic Landing Engine', 'desc': 'Tạo trang Landing Page siêu nhẹ (<50KB) load mượt'},
                    {'id': 'eng_markitdown', 'name': 'Microsoft MarkItDown', 'desc': 'Bóc tách file Excel/Word sản phẩm từ máy tính'},
                    {'id': 'eng_seo', 'name': 'Google SEO Top Ranking', 'desc': 'Viết bài chuẩn SEO Top 1 Google & Sitemap XML'},
                    {'id': 'eng_video', 'name': 'AI Video Generator', 'desc': 'Tự động tạo Video ngắn Reels/TikTok 1080x1920'},
                    {'id': 'eng_buzz', 'name': 'Block Buzz Hive-Mind', 'desc': 'Phát sóng tín hiệu sự kiện thời gian thực giữa 10 AI Agents'}
                ]
            },
            {
                'name': '4. Data & Infrastructure Tier (Lưu trữ & Hạ tầng)',
                'components': [
                    {'id': 'db_sqlite', 'name': 'SQLite Database', 'type': 'Database', 'desc': 'database.db với cấu trúc Indexes tối ưu hoá'},
                    {'id': 'playwright_engine', 'name': 'Playwright Virtual Browsers', 'type': 'Browser Automation', 'desc': 'Chạy 10 trình duyệt ảo Chromium ngầm'}
                ]
            }
        ]
    }
    
    # Generate Interactive HTML/SVG C4 Visualizer Page
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LikeC4 Interactive System Architecture - HAME Enterprise v29.0</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #f1f5f9; padding: 30px; line-height: 1.6; }}
        .header {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #1e293b; padding-bottom: 20px; }}
        h1 {{ color: #38bdf8; font-size: 2.2rem; margin-bottom: 8px; }}
        p.subtitle {{ color: #94a3b8; font-size: 1.1rem; }}
        .tier-box {{ background: #1e293b; border-radius: 16px; padding: 24px; margin-bottom: 30px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .tier-title {{ font-size: 1.4rem; color: #f59e0b; margin-bottom: 16px; border-bottom: 1px solid #334155; padding-bottom: 8px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
        .card {{ background: #0f172a; border-radius: 12px; padding: 18px; border: 1px solid #334155; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-4px); border-color: #38bdf8; }}
        .card-title {{ font-weight: bold; font-size: 1.1rem; color: #38bdf8; margin-bottom: 6px; }}
        .card-desc {{ color: #cbd5e1; font-size: 0.95rem; }}
        .badge {{ display: inline-block; background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📐 LIKEC4 INTERACTIVE ARCHITECTURE VISUALIZER</h1>
        <p class="subtitle">Sơ Đồ Kiến Trúc Tổng Thể Cỗ Máy HAME Enterprise Suite v29.0 (100% Autonomous AI Matrix)</p>
    </div>
"""
    
    for tier in c4_model['tiers']:
        cards_html = ""
        for comp in tier['components']:
            ctype = f"<span class='badge'>{comp.get('type', 'Module')}</span><br>" if 'type' in comp else ""
            cards_html += f"""
            <div class="card">
                {ctype}
                <div class="card-title">{comp['name']}</div>
                <div class="card-desc">{comp['desc']}</div>
            </div>
            """
        html_content += f"""
        <div class="tier-box">
            <div class="tier-title">{tier['name']}</div>
            <div class="grid">
                {cards_html}
            </div>
        </div>
        """
        
    html_content += """
</body>
</html>
"""
    
    file_path = os.path.join(ARCH_DIR, 'architecture.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"   📐 [LikeC4 Visualizer] Đã xuất bản sơ đồ C4 tương tác tại: http://localhost:5000/architecture")
    
    return {'status': 'success', 'architecture_url': 'http://localhost:5000/architecture', 'model': c4_model}

def export_likec4_dsl():
    """Xuất bản đặc tả mã C4 DSL chuẩn LikeC4."""
    dsl_text = """
specification {
  element system
  element container
  element component
}

model {
  hame_suite = system 'HAME Enterprise Suite v29.0' {
    pwa = container 'PWA Mobile App Client'
    dashboard = container 'Web Admin Dashboard'
    matrix_agents = container 'Autonomous 10-Nick AI Agent Squad'
    core_engines = container 'Core Intelligence AI Engines'
    db = container 'SQLite Database database.db'
  }
}
"""
    return dsl_text

if __name__ == '__main__':
    generate_likec4_architecture()

