import sqlite3, json, sys

sys.stdout.reconfigure(encoding='utf-8')

# High-converting Affiliate Recommendation Matrix (Cross-Sell Rules)
RECOMMENDATION_MATRIX = {
    'balo': [
        {
            'title': '☔ Hạt Bọc Túi Trùm Balo Chống Nước Tuyệt Đối ShopeeMall',
            'url': 'https://shopee.vn/product/111/222',
            'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F111%2F222&affiliate_id=783489745',
            'reason': 'Phụ kiện chống mưa bảo vệ laptop không thể thiếu khi mua balo.'
        },
        {
            'title': '🎧 Tai Nghe Bluetooth Gaming Chống Ồn Chế Độ Âm Thanh Siêu Trầm',
            'url': 'https://shopee.vn/product/333/444',
            'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F333%2F444&affiliate_id=783489745',
            'reason': 'Phụ kiện công nghệ hot combo đi kèm balo laptop.'
        }
    ],
    'sneaker': [
        {
            'title': '🧦 Bộ 5 Đôi Tất Cổ Ngắn Cotton Thấm Mút Mồ Hôi Cao Cấp',
            'url': 'https://shopee.vn/product/555/666',
            'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F555%2F666&affiliate_id=783489745',
            'reason': 'Combo đi kèm bọc chân êm ái khi mua sneaker.'
        },
        {
            'title': '✨ Chai Xịt Tẩy Rửa Vệ Sinh Giày Sneaker Nhanh Siêu Sạch',
            'url': 'https://shopee.vn/product/777/888',
            'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F777%2F888&affiliate_id=783489745',
            'reason': 'Giữ giày luôn như mới sau khi sử dụng.'
        }
    ],
    'gia dung': [
        {
            'title': '📦 Bộ 3 Hộp Thuỷ Tinh Chịu Nhiệt Lò Vi Sóng Cao Cấp LazadaMall',
            'url': 'https://s.lazada.vn/s.9999',
            'aff_url': 'https://s.lazada.vn/s.9999?custom_id=201037552823',
            'reason': 'Combo làm bếp giữ an toàn vệ sinh cho gia đình.'
        }
    ],
    'thoi trang': [
        {
            'title': '👜 Túi Da Cầm Tay Mini Nữ Sang Chảnh Phối Áo Đầm',
            'url': 'https://shopee.vn/product/999/000',
            'aff_url': 'https://s.shopee.vn/an_redir?origin_link=https%3A%2F%2Fshopee.vn%2Fproduct%2F999%2F000&affiliate_id=783489745',
            'reason': 'Phụ kiện tôn dáng cực đẹp khi diện đầm thiết kế.'
        }
    ]
}

def get_smart_recommendations(product_title_or_category):
    """
    Phân tích từ khoá sản phẩm và trả về danh sách 2-3 sản phẩm gợi ý bán chéo (Cross-Sell)
    có tỉ lệ chốt đơn cao nhất kèm Link Affiliate.
    """
    title_lower = (product_title_or_category or '').lower()
    
    recommended_items = []
    for category_kw, items in RECOMMENDATION_MATRIX.items():
        if category_kw in title_lower:
            recommended_items.extend(items)
            
    if not recommended_items:
        # Fallback to Balo + Voucher deals
        recommended_items = RECOMMENDATION_MATRIX['balo']
        
    return {
        'status': 'success',
        'query': product_title_or_category,
        'count': len(recommended_items),
        'recommendations': recommended_items
    }

if __name__ == '__main__':
    test_res = get_smart_recommendations('Balo laptop nam chống nước')
    print("=== AI RECOMMENDATION ENGINE TEST ===")
    print(json.dumps(test_res, ensure_ascii=False, indent=2))
