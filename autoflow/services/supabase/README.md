# Supabase 資料庫設計

## 資料庫連線配置

```python
DB_CONFIG = {
    'url': 'SUPABASE_URL',
    'key': 'SUPABASE_KEY',
    'options': {
        'schema': 'public',
        'headers': {
            'apikey': 'SUPABASE_KEY',
            'Authorization': 'Bearer SUPABASE_KEY'
        }
    }
}
```

## 資料表結構

### 1. 用戶表 (users)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

欄位說明：
- `id`: 用戶唯一識別碼
- `telegram_id`: Telegram 用戶 ID
- `username`: Telegram 用戶名
- `first_name`: 用戶名字
- `last_name`: 用戶姓氏
- `created_at`: 創建時間
- `updated_at`: 更新時間

### 2. 對話記錄表 (conversations)

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    message TEXT,
    response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

欄位說明：
- `id`: 對話記錄唯一識別碼
- `user_id`: 關聯到用戶表的外鍵
- `message`: 用戶發送的消息
- `response`: 機器人的回應（Markdown 格式）
- `created_at`: 創建時間

### 3. 圖片表 (images)

```sql
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id),
    image_data BYTEA,
    image_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

欄位說明：
- `id`: 圖片唯一識別碼
- `conversation_id`: 關聯到對話記錄表的外鍵
- `image_data`: 圖片二進制數據
- `image_type`: 圖片類型（如 'png', 'jpg' 等）
- `created_at`: 創建時間

## 索引設計

```sql
-- 用戶表索引
CREATE INDEX idx_users_telegram_id ON users(telegram_id);

-- 對話記錄表索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

-- 圖片表索引
CREATE INDEX idx_images_conversation_id ON images(conversation_id);
```

## 使用範例

### 1. 創建用戶

```python
user = await supabase.create_user(
    telegram_id=123456789,
    username="example_user",
    first_name="John",
    last_name="Doe"
)
```

### 2. 創建對話記錄

```python
conversation = await supabase.create_conversation(
    user_id=user['id'],
    message="AAPL",
    response="📊 AAPL 股票行情\n\n最新價格：$150.00"
)
```

### 3. 保存圖片

```python
image = await supabase.save_image(
    conversation_id=conversation['id'],
    image_data=image_bytes,
    image_type="png"
)
```

## 注意事項

1. 環境變數設置
   - 需要在 `.env` 文件中設置 `SUPABASE_URL` 和 `SUPABASE_KEY`
   - 確保環境變數的安全性

2. 資料備份
   - 定期備份資料庫
   - 使用 Supabase 的備份功能

3. 效能優化
   - 使用適當的索引
   - 定期清理過期數據
   - 監控資料庫效能

4. 安全性
   - 使用 Row Level Security (RLS)
   - 實施適當的訪問控制
   - 加密敏感數據 