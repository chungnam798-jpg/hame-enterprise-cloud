import urllib.request
import json
import sys

BASE_URL = 'http://localhost:5000/api'

def test_api():
    print("Starting integration test for FBPoster v1.1 APIs...")
    
    # 1. Test GET /settings
    try:
        req = urllib.request.Request(f"{BASE_URL}/settings")
        with urllib.request.urlopen(req) as r:
            settings = json.loads(r.read().decode('utf-8'))
            print("[OK] GET /settings:", settings)
            assert 'delay_between_posts' in settings
    except Exception as e:
        print("[FAIL] GET /settings:", e)
        sys.exit(1)
        
    # 2. Test POST /settings
    try:
        data = json.dumps({'delay_between_posts': '45', 'engage_interval_minutes': '12'}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/settings", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode('utf-8'))
            print("[OK] POST /settings:", res)
            assert res.get('delay_between_posts') == '45'
    except Exception as e:
        print("[FAIL] POST /settings:", e)
        sys.exit(1)

    # 3. Test POST /accounts
    account_id = None
    try:
        data = json.dumps({'name': 'Test Account Py', 'cookie': 'c_user=12345; xs=abc;', 'status': 'active'}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/accounts", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode('utf-8'))
            print("[OK] POST /accounts:", res)
            assert 'id' in res
            account_id = res['id']
    except Exception as e:
        print("[FAIL] POST /accounts:", e)
        sys.exit(1)

    # 4. Test GET /accounts
    try:
        req = urllib.request.Request(f"{BASE_URL}/accounts")
        with urllib.request.urlopen(req) as r:
            accounts = json.loads(r.read().decode('utf-8'))
            print("[OK] GET /accounts: found", len(accounts), "accounts")
            assert len(accounts) > 0
    except Exception as e:
        print("[FAIL] GET /accounts:", e)
        sys.exit(1)

    # 5. Test POST /templates
    template_id = None
    try:
        data = json.dumps({'name': 'Test Template', 'content': 'This is a test content with {keyword}', 'tags': 'test,api'}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/templates", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode('utf-8'))
            print("[OK] POST /templates:", res)
            assert res.get('success') is True
            template_id = res.get('id')
    except Exception as e:
        print("[FAIL] POST /templates:", e)
        sys.exit(1)

    # 6. Test GET /templates
    try:
        req = urllib.request.Request(f"{BASE_URL}/templates")
        with urllib.request.urlopen(req) as r:
            templates = json.loads(r.read().decode('utf-8'))
            print("[OK] GET /templates: found", len(templates), "templates")
            assert len(templates) > 0
    except Exception as e:
        print("[FAIL] GET /templates:", e)
        sys.exit(1)

    # 7. Test POST /engagement/rules
    rule_id = None
    try:
        data = json.dumps({'keywords': 'test,api', 'reply_text': 'This is an auto reply for test'}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/engagement/rules", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode('utf-8'))
            print("[OK] POST /engagement/rules:", res)
            assert 'id' in res
            rule_id = res['id']
    except Exception as e:
        print("[FAIL] POST /engagement/rules:", e)
        sys.exit(1)

    # 8. Test POST /autolike/targets
    target_id = None
    try:
        data = json.dumps({'account_id': account_id, 'target_url': 'https://facebook.com/groups/test', 'target_name': 'Test Group'}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/autolike/targets", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode('utf-8'))
            print("[OK] POST /autolike/targets:", res)
            assert res.get('success') is True
            target_id = res.get('id')
    except Exception as e:
        print("[FAIL] POST /autolike/targets:", e)
        sys.exit(1)

    # 9. Test GET /analytics
    try:
        req = urllib.request.Request(f"{BASE_URL}/analytics")
        with urllib.request.urlopen(req) as r:
            analytics = json.loads(r.read().decode('utf-8'))
            print("[OK] GET /analytics:", analytics)
            assert 'post_stats' in analytics
    except Exception as e:
        print("[FAIL] GET /analytics:", e)
        sys.exit(1)

    # Clean up test entities
    print("Cleaning up test entities...")
    try:
        if template_id:
            req = urllib.request.Request(f"{BASE_URL}/templates/{template_id}", method='DELETE')
            urllib.request.urlopen(req)
        if rule_id:
            req = urllib.request.Request(f"{BASE_URL}/engagement/rules/{rule_id}", method='DELETE')
            urllib.request.urlopen(req)
        if target_id:
            req = urllib.request.Request(f"{BASE_URL}/autolike/targets/{target_id}", method='DELETE')
            urllib.request.urlopen(req)
        if account_id:
            req = urllib.request.Request(f"{BASE_URL}/accounts/{account_id}", method='DELETE')
            urllib.request.urlopen(req)
        print("[OK] Cleanup completed successfully.")
    except Exception as e:
        print("[WARNING] Cleanup failed:", e)

    print("\n>>> ALL API INTEGRATION TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    test_api()
