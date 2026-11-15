import sqlite3, os
DB_PATH = os.path.join('database.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ensure autolike_targets table exists and get its columns
cursor.execute('PRAGMA table_info(autolike_targets)')
cols = [row[1] for row in cursor.fetchall()]
# Expected columns (example): id, target_id, type, name, comment_text, cross_comment_enabled
# Insert the group if not already present
group_id = '158992923718361'
# Check existence
cursor.execute('SELECT COUNT(*) FROM autolike_targets WHERE target_id = ?', (group_id,))
exists = cursor.fetchone()[0]
if not exists:
    # Prepare minimal fields; adjust according to actual schema
    # Use placeholder values for name and comment_text if missing
    name = 'Group 158992923718361'
    comment_text = "💬 {emoji} Sản phẩm hot tại {group_name}! Xem ngay: {link}"
    # Build insert statement based on available columns
    fields = []
    values = []
    if 'target_id' in cols:
        fields.append('target_id')
        values.append(group_id)
    if 'type' in cols:
        fields.append('type')
        values.append('group')
    if 'name' in cols:
        fields.append('name')
        values.append(name)
    if 'comment_text' in cols:
        fields.append('comment_text')
        values.append(comment_text)
    if 'cross_comment_enabled' in cols:
        fields.append('cross_comment_enabled')
        values.append(1)
    placeholders = ','.join(['?'] * len(values))
    sql = f"INSERT INTO autolike_targets ({','.join(fields)}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(values))
    print(f'Inserted group {group_id} into autolike_targets')
else:
    print(f'Group {group_id} already exists in autolike_targets')

conn.commit()
conn.close()
