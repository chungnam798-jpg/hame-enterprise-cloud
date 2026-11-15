import sqlite3, json, sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

raw_cookies = [
  {"domain": ".affiliate.shopee.vn", "expirationDate": 1787535207, "hostOnly": False, "httpOnly": False, "name": "_QPWSDCXHZQA", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "7792c649-cd20-4bcc-a2ed-aaf061cb160f", "id": 1},
  {"domain": ".affiliate.shopee.vn", "expirationDate": 1787535265, "hostOnly": False, "httpOnly": False, "name": "ds", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "a8c9c7dae60b7d15ce0dc63e89dfd31d", "id": 2},
  {"domain": ".affiliate.shopee.vn", "expirationDate": 1787535264, "hostOnly": False, "httpOnly": False, "name": "REC7iLP4Q", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "73aeef7c-e435-4370-a48e-5325375cc6bd", "id": 3},
  {"domain": ".affiliate.shopee.vn", "expirationDate": 1787535265, "hostOnly": False, "httpOnly": False, "name": "shopee_webUnique_ccd", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "TsdLSMqf%2BIaWJZ3vKQMzMA%3D%3D%7CsBAXvuMkLLIikKSQbO6JwODBHMvb9XsA02PvTd75VkjUO%2FlOXNlM1e%2BRMrpnu1FcB4JO9GX38Zu82w%3D%3D%7CyyMrvy2W78Mvzl6Z%7C08%7C3", "id": 4},
  {"domain": ".shopee.vn", "expirationDate": 1792719265, "hostOnly": False, "httpOnly": False, "name": "_fbp", "path": "/", "sameSite": "lax", "secure": False, "session": False, "storeId": "0", "value": "fb.1.1784943228017.52626306770647856", "id": 5},
  {"domain": ".shopee.vn", "expirationDate": 1819503263.217542, "hostOnly": False, "httpOnly": False, "name": "_ga", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "GA1.1.1630387211.1784943207", "id": 6},
  {"domain": ".shopee.vn", "expirationDate": 1819503263.270242, "hostOnly": False, "httpOnly": False, "name": "_ga_4GPP1ZXG63", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "GS2.1.s1784943207$o1$g1$t1784943263$j4$l0$h1792479858", "id": 7},
  {"domain": ".shopee.vn", "expirationDate": 1792719202, "hostOnly": False, "httpOnly": False, "name": "_gcl_au", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "1.1.1928858051.1784943202", "id": 8},
  {"domain": ".shopee.vn", "expirationDate": 1787535231, "hostOnly": False, "httpOnly": False, "name": "_med", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "affiliates", "id": 9},
  {"domain": ".shopee.vn", "expirationDate": 1787535229, "hostOnly": False, "httpOnly": False, "name": "_QPWSDCXHZQA", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "1814aed5-1135-4c71-ac51-7dac9956a2c3", "id": 10},
  {"domain": ".shopee.vn", "hostOnly": False, "httpOnly": False, "name": "csrftoken", "path": "/", "sameSite": "unspecified", "secure": False, "session": True, "storeId": "0", "value": "ze9IMldxVJsSG7wBQrvSpIdKnErYWnlR", "id": 11},
  {"domain": ".shopee.vn", "expirationDate": 1787535260, "hostOnly": False, "httpOnly": False, "name": "ds", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "0e4a7541cb8ddfab53402c97bab9cbe5", "id": 12},
  {"domain": ".shopee.vn", "expirationDate": 1819503226.4178, "hostOnly": False, "httpOnly": False, "name": "language", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "vi", "id": 13},
  {"domain": ".shopee.vn", "expirationDate": 1819503227.902986, "hostOnly": False, "httpOnly": True, "name": "REC_T_ID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "e28311c4-87c8-11f1-a1c1-9a9a2200fb0d", "id": 14},
  {"domain": ".shopee.vn", "expirationDate": 1787535233, "hostOnly": False, "httpOnly": False, "name": "REC7iLP4Q", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "9abd440b-3b1b-438d-bb61-b7b0bfc9b142", "id": 15},
  {"domain": ".shopee.vn", "hostOnly": False, "httpOnly": False, "name": "sense_sa_r", "path": "/", "sameSite": "unspecified", "secure": False, "session": True, "storeId": "0", "value": "s", "id": 16},
  {"domain": ".shopee.vn", "expirationDate": 1787535260, "hostOnly": False, "httpOnly": False, "name": "shopee_webUnique_ccd", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "5D%2FMryzVqHRU1hP000BNWA%3D%3D%7CtRAXvu8pJ5sGkKSQbO6JwODBHMvb9XsA02PvTT2GVkjUO%2FlOXNlM1e%2BRMrpnu1FcB4JO9GX38Zu8WzM%3D%7CyyMrvy2W78Mvzl6Z%7C08%7C3", "id": 17},
  {"domain": ".shopee.vn", "expirationDate": 1819503258.98717, "hostOnly": False, "httpOnly": False, "name": "SPC_CLIENTID", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "bkY0ZmFGZGhJYll1awylsypjbaulpkyp", "id": 18},
  {"domain": ".shopee.vn", "expirationDate": 1819503227.902933, "hostOnly": False, "httpOnly": False, "name": "SPC_F", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "nF4faFdhIbYucByugOGLwgVwpU0gy8cl", "id": 19},
  {"domain": ".shopee.vn", "expirationDate": 1819503258.987324, "hostOnly": False, "httpOnly": False, "name": "SPC_R_T_ID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "PFTZdjWWOjZ7eovU9zQmZy36rrihHEVzEu4MPE6nGVb7AV+P/JPoO4vE8tRu/XW4iPkFP0k8oZ13yJ32DJu+CvdNqsnQNzKnwuYN2w9xBuKYuyYv3xwdUbhqHvDV471uhwrkO0t15WnaSHg0fQVUImXj4RTIAF87g6EMJjn4B9E=", "id": 20},
  {"domain": ".shopee.vn", "expirationDate": 1819503258.987379, "hostOnly": False, "httpOnly": False, "name": "SPC_R_T_IV", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "cVhhMHJ5eVIyRDBiS3VxTQ==", "id": 21},
  {"domain": ".shopee.vn", "expirationDate": 1785029658.98727, "hostOnly": False, "httpOnly": True, "name": "SPC_SI", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "W3YnagAAAABNSldCS2V2OaOMUgMAAAAAaEdaMjYzdFo=", "id": 22},
  {"domain": ".shopee.vn", "expirationDate": 1819503258.987205, "hostOnly": False, "httpOnly": True, "name": "SPC_ST", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "UmtxaGdUaFVHbzRQQk9lbqFF5LNEFLXT0I5zYPfFhYRQblGe8vLRKz5j9a2lSRThl7pMRJ70LT93eno3NwpGUk+nHO7NqVE2O9itHWssgD4Y8IxggsIy2Um7T2/3KEE37lmlV6qZqpNc56w4JcoiNwIxBLYsOTBljmTfwqhAflepM/E1LYGhENaHpzWApfvOcB+c/dfvUxg2KDQ9YE8SPA==.ALBemtfAW6VdUvyCBf/vLFyevNAJZKxhDrEo6QOWQa2t", "id": 23},
  {"domain": ".shopee.vn", "expirationDate": 1819503258.986942, "hostOnly": False, "httpOnly": True, "name": "SPC_T_ID", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "PFTZdjWWOjZ7eovU9zQmZy36rrihHEVzEu4MPE6nGVb7AV+P/JPoO4vE8tRu/XW4iPkFP0k8oZ13yJ32DJu+CvdNqsnQNzKnwuYN2w9xBuKYuyYv3xwdUbhqHvDV471uhwrkO0t15WnaSHg0fQVUImXj4RTIAF87g6EMJjn4B9E=", "id": 24},
  {"domain": ".shopee.vn", "expirationDate": 1819503258.987082, "hostOnly": False, "httpOnly": True, "name": "SPC_T_IV", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "cVhhMHJ5eVIyRDBiS3VxTQ==", "id": 25},
  {"domain": ".shopee.vn", "expirationDate": 1819503258.987238, "hostOnly": False, "httpOnly": False, "name": "SPC_U", "path": "/", "sameSite": "unspecified", "secure": True, "session": False, "storeId": "0", "value": "783489745", "id": 26},
  {"domain": ".shopee.vn", "expirationDate": 1787535227, "hostOnly": False, "httpOnly": False, "name": "ssr-tz", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "Asia/Saigon", "id": 27},
  {"domain": "affiliate.shopee.vn", "expirationDate": 1816479207, "hostOnly": True, "httpOnly": False, "name": "_QPWSDCXHZQA", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "7792c649-cd20-4bcc-a2ed-aaf061cb160f", "id": 28},
  {"domain": "affiliate.shopee.vn", "hostOnly": True, "httpOnly": False, "name": "_sapid", "path": "/", "sameSite": "unspecified", "secure": False, "session": True, "storeId": "0", "value": "edfffe754ded9a1fe8a2327790aac2ee7ad6b5d564fa5fd162be3c03", "id": 29},
  {"domain": "affiliate.shopee.vn", "expirationDate": 1816479265, "hostOnly": True, "httpOnly": False, "name": "ds", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "a8c9c7dae60b7d15ce0dc63e89dfd31d", "id": 30},
  {"domain": "affiliate.shopee.vn", "hostOnly": True, "httpOnly": False, "name": "language", "path": "/", "sameSite": "unspecified", "secure": False, "session": True, "storeId": "0", "value": "vi", "id": 31},
  {"domain": "affiliate.shopee.vn", "expirationDate": 1816479264, "hostOnly": True, "httpOnly": False, "name": "REC7iLP4Q", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "73aeef7c-e435-4370-a48e-5325375cc6bd", "id": 32},
  {"domain": "affiliate.shopee.vn", "expirationDate": 1816479265, "hostOnly": True, "httpOnly": False, "name": "shopee_webUnique_ccd", "path": "/", "sameSite": "unspecified", "secure": False, "session": False, "storeId": "0", "value": "TsdLSMqf%2BIaWJZ3vKQMzMA%3D%3D%7CsBAXvuMkLLIikKSQbO6JwODBHMvb9XsA02PvTd75VkjUO%2FlOXNlM1e%2BRMrpnu1FcB4JO9GX38Zu82w%3D%3D%7CyyMrvy2W78Mvzl6Z%7C08%7C3", "id": 33}
]

# Extract SPC_U (Affiliate User ID)
spc_u = "783489745"
json_cookie_str = json.dumps(raw_cookies)

cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shopee_affiliate_id', ?)", (spc_u,))
cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shopee_cookie', ?)", (json_cookie_str,))

# Construct cookie string format
cookie_header_str = "; ".join([f"{c['name']}={c['value']}" for c in raw_cookies if 'name' in c and 'value' in c])
cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shopee_cookie_header', ?)", (cookie_header_str,))

conn.commit()
print("SUCCESSFULLY INTEGRATED SHOPEE AFFILIATE COOKIE & USER ID:")
print("Shopee Affiliate ID:", spc_u)
print("Cookie Count:", len(raw_cookies))
print("Cookie Header Length:", len(cookie_header_str))

conn.close()
