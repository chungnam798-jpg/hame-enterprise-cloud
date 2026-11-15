import sys
import os
import argparse
from scrape_group_members import scrape_members
from auto_dm_playwright import run_dm_campaign

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group_url', required=True)
    parser.add_argument('--product_url', default='')
    parser.add_argument('--industry', default='thoi_trang')
    parser.add_argument('--high_risk', action='store_true')
    args = parser.parse_args()

    if args.product_url:
        os.environ['PRODUCT_URL'] = args.product_url
    if args.industry:
        os.environ['DM_INDUSTRY'] = args.industry

    print(f"Bắt đầu chiến dịch Auto DM ({args.industry}) cho nhóm: {args.group_url}")
    if scrape_members(args.group_url, high_risk_mode=args.high_risk):
        print("Bắt đầu nhắn tin...")
        run_dm_campaign()
    else:
        print("Không tìm thấy thành viên hoặc lỗi khi quét.")

if __name__ == '__main__':
    main()
