import sqlite3, json, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

raw_lazada_cookies = [
  {"domain": ".lazada.vn", "expirationDate": 1785548285.087195, "hostOnly": False, "httpOnly": False, "name": "_m_h5_tk", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "67a81c2e1ba758e39d7c11fef8ee4fbf_1784953925729", "id": 1},
  {"domain": ".lazada.vn", "expirationDate": 1785548285.087368, "hostOnly": False, "httpOnly": False, "name": "_m_h5_tk_enc", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "4a047d96c7e2ee125b762fd41082238d", "id": 2},
  {"domain": ".lazada.vn", "hostOnly": False, "httpOnly": True, "name": "_tb_token_", "path": "/", "sameSite": "no_restriction", "secure": True, "session": True, "storeId": "0", "value": "eb913bf34eae7", "id": 3},
  {"domain": ".lazada.vn", "expirationDate": 1819503480.977094, "hostOnly": False, "httpOnly": False, "name": "cna", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "cAHrIhS/2wQCAavlDiUnYNnE", "id": 4},
  {"domain": ".lazada.vn", "expirationDate": 1800495556.817346, "hostOnly": False, "httpOnly": False, "name": "epssw", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "13*HAr4zOGGGIGofwrOV-pRwrjO52pGw-5zwcJzlr8HlGFHB_wM6My5AMj5aD5kV_86V-IRGyStlOLAv37EmyOOwy4gmAsNgZl-6NQqF3VNNPQcKUjGUNeSQrMOjOH_8Mq5tGHEyztHSMj1CGW9O38-JgzEs4_RiXF5hiekhPyr9wuOwQTjyieujRQU9GFdihOrorejIoZAyipdwMsRB13iMgdwavYGYf1338UbSGRWrCGHrbo_46RRya0M4U-GGBg36XQ-UIRMTMIIccnf89B04HkV46GGGH9Ib7jfGHChzX8GK6KJHBMKyk4GGOwOybW3YOrHe5pIi7FOB1BPDlWzSoSeAvC9Srygg7qSnOUT6GuHbQk6GAP2QMOwQGGGy7KGGGObVWRW", "id": 5},
  {"domain": ".lazada.vn", "expirationDate": 1787535470, "hostOnly": False, "httpOnly": False, "name": "hng", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "VN|en|VND|704", "id": 6},
  {"domain": ".lazada.vn", "expirationDate": 1800495553, "hostOnly": False, "httpOnly": False, "name": "isg", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "BGJi3ry3fNlb42CFz-fjAlOfs-jEs2bNSd1F-qz7hVWAfwL5lECX3ar9q6OD795l", "id": 7},
  {"domain": ".lazada.vn", "expirationDate": 1800495553.324303, "hostOnly": False, "httpOnly": False, "name": "lwrid", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "AgGfluvoKlLlVJcLsQ52X39uIxeK", "id": 8},
  {"domain": ".lazada.vn", "expirationDate": 1800495522.670107, "hostOnly": False, "httpOnly": False, "name": "lwrtk", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "AAIEamSEIhyZoIFtox2eyRh9uqDlfrJiZ43SFT7VDjOSXJb6NDpdRp8=", "id": 9},
  {"domain": ".lazada.vn", "hostOnly": False, "httpOnly": True, "name": "lzd_b_csg", "path": "/", "sameSite": "no_restriction", "secure": True, "session": True, "storeId": "0", "value": "9bc0852e", "id": 10},
  {"domain": ".lazada.vn", "expirationDate": 1816508272.761676, "hostOnly": False, "httpOnly": False, "name": "lzd_cid", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "f12364c8-0d6e-41d4-96a0-099027b78654", "id": 11},
  {"domain": ".lazada.vn", "expirationDate": 1816479552, "hostOnly": False, "httpOnly": False, "name": "lzd_login_lastlogintype", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "QR_CODE_LOGIN", "id": 12},
  {"domain": ".lazada.vn", "hostOnly": False, "httpOnly": True, "name": "lzd_sid", "path": "/", "sameSite": "no_restriction", "secure": True, "session": True, "storeId": "0", "value": "1daa66eace451b9e5166f62edf44142f", "id": 13},
  {"domain": ".lazada.vn", "hostOnly": False, "httpOnly": False, "name": "lzd_uid", "path": "/", "sameSite": "no_restriction", "secure": True, "session": True, "storeId": "0", "value": "201037552823", "id": 14},
  {"domain": ".lazada.vn", "hostOnly": False, "httpOnly": False, "name": "lzd_uti", "path": "/", "sameSite": "no_restriction", "secure": True, "session": True, "storeId": "0", "value": "%7B%22fpd%22%3A%229999-99-99%22%2C%22lpd%22%3A%229999-99-99%22%2C%22cnt%22%3A%220%22%7D", "id": 15},
  {"domain": ".lazada.vn", "expirationDate": 1787564352.134454, "hostOnly": False, "httpOnly": True, "name": "sgcookie", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "E100YKGbSm15u%2FmVMCfRWwkw%2FQuGP%2BZjncA5XIzxzq3PuLODz5rgzVsAj7q9LdY5GLXoGAMgJh0Y7Vapyec4oQZmgY5pLqJ4O5fFy%2B7%2BY%2FoA7Qo%3D", "id": 16},
  {"domain": ".lazada.vn", "expirationDate": 1819503468.709829, "hostOnly": False, "httpOnly": False, "name": "t_fv", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "1784943468709", "id": 17},
  {"domain": ".lazada.vn", "expirationDate": 1784945353, "hostOnly": False, "httpOnly": False, "name": "t_sid", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "8D2zoyqgsn2TpTBOu0bhASwFbVuDBmdk", "id": 18},
  {"domain": ".lazada.vn", "expirationDate": 1819503468.710634, "hostOnly": False, "httpOnly": False, "name": "t_uid", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "PJakumAGsCp72MQcEViFZrmkgcS92dJu", "id": 19},
  {"domain": ".lazada.vn", "expirationDate": 1800495553, "hostOnly": False, "httpOnly": False, "name": "tfstk", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "gsaxwzi5aTX05V75pEjuIhvo395ukgV2m-PBSADDf8e8OWJmfRjVfVeUBctgsqO44JVBorjqSF3q7V6hKwbtgSuZ5AS98KM4N7l1ZjwSCcbi7V6hE743bU3anPYAdcN5wfcICFws1aTSUfpXfRMjVLGKTVM_CRGSPXG6cAGj1YiSUfgsCRg1w7Mr6VM_CV18Nj7wMAAjBFEk0HGMRpGe5Fa-M0_3GYTqOzhxDvNbkFT6YjnxdoM5nUqlT0NZXPRwWDVbYRlQhK6tQzF7lkwCEnDbvfF3XJQB7brbHziTr17LaqhtAViJ1FN-PAiLr2_Bebr7ila4HCLsgr4nXvoR1FoiPymQA-dNT7gj1RoUS98qh5NU8k0dkplYVW3R4a43J9_2KvhMc_CJbhoja8a5ItHCx3qrwvfkqh-Zqbl-K_CJbhojabHhZ3xwb0cP.", "id": 20},
  {"domain": ".lazada.vn", "expirationDate": 1784945353, "hostOnly": False, "httpOnly": False, "name": "utm_channel", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "Referral", "id": 21},
  {"domain": ".lazada.vn", "expirationDate": 1784945353, "hostOnly": False, "httpOnly": False, "name": "utm_r_cm", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "Lazada 23.6.2026", "id": 22},
  {"domain": ".lazada.vn", "expirationDate": 1784945353, "hostOnly": False, "httpOnly": False, "name": "utm_r_cn", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "45380778?", "id": 23},
  {"domain": ".lazada.vn", "expirationDate": 1784945353, "hostOnly": False, "httpOnly": False, "name": "utm_r_m", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "CPC", "id": 24},
  {"domain": ".lazada.vn", "expirationDate": 1784945353, "hostOnly": False, "httpOnly": False, "name": "utm_r_s", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "coccoc_context", "id": 25},
  {"domain": ".lazada.vn", "expirationDate": 1784945353, "hostOnly": False, "httpOnly": False, "name": "utm_r_t", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "lazada", "id": 26},
  {"domain": ".lazada.vn", "expirationDate": 1785202701, "hostOnly": False, "httpOnly": False, "name": "xlly_s", "path": "/", "sameSite": "no_restriction", "secure": True, "session": False, "storeId": "0", "value": "1", "id": 27},
  {"domain": "www.lazada.vn", "expirationDate": 1787535470, "hostOnly": True, "httpOnly": False, "name": "userLanguageML", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "en", "id": 28}
]

# Extract lzd_uid (Lazada User ID)
lzd_uid = "201037552823"
json_lzd_cookie_str = json.dumps(raw_lazada_cookies)

cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('lazada_affiliate_id', ?)", (lzd_uid,))
cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('lazada_cookie', ?)", (json_lzd_cookie_str,))

cookie_header_str = "; ".join([f"{c['name']}={c['value']}" for c in raw_lazada_cookies if 'name' in c and 'value' in c])
cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('lazada_cookie_header', ?)", (cookie_header_str,))

conn.commit()
print("SUCCESSFULLY INTEGRATED LAZADA AFFILIATE COOKIE & USER ID:")
print("Lazada User ID:", lzd_uid)
print("Cookie Count:", len(raw_lazada_cookies))
print("Cookie Header Length:", len(cookie_header_str))

conn.close()
