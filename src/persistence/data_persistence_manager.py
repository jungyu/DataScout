for key, value in filter_query.items():
            if isinstance(value, str):
                notion_filter["and"].append({
                    "property": key,
                    "rich_text": {
                        "contains": value
                    }
                })
            elif isinstance(value, int) or isinstance(value, float):
                notion_filter["and"].append({
                    "property": key,
                    "number": {
                        "equals": value
                    }
                })
            elif isinstance(value, bool):
                notion_filter["and"].append({
                    "property": key,
                    "checkbox": {
                        "equals": value
                    }
                })
            elif isinstance(value, dict):
                # 處理運算符
                for op, op_value in value.items():
                    if op == "eq":
                        if isinstance(op_value, str):
                            notion_filter["and"].append({
                                "property": key,
                                "rich_text": {
                                    "equals": op_value
                                }
                            })
                        else:
                            notion_filter["and"].append({
                                "property": key,
                                "number": {
                                    "equals": op_value
                                }
                            })
                    elif op == "ne":
                        if isinstance(op_value, str):
                            notion_filter["and"].append({
                                "property": key,
                                "rich_text": {
                                    "does_not_equal": op_value
                                }
                            })
                        else:
                            notion_filter["and"].append({
                                "property": key,
                                "number": {
                                    "does_not_equal": op_value
                                }
                            })
                    elif op == "gt":
                        notion_filter["and"].append({
                            "property": key,
                            "number": {
                                "greater_than": op_value
                            }
                        })
                    elif op == "gte":
                        notion_filter["and"].append({
                            "property": key,
                            "number": {
                                "greater_than_or_equal_to": op_value
                            }
                        })
                    elif op == "lt":
                        notion_filter["and"].append({
                            "property": key,
                            "number": {
                                "less_than": op_value
                            }
                        })
                    elif op == "lte":
                        notion_filter["and"].append({
                            "property": key,
                            "number": {
                                "less_than_or_equal_to": op_value
                            }
                        })
                    elif op == "contains":
                        notion_filter["and"].append({
                            "property": key,
                            "rich_text": {
                                "contains": op_value
                            }
                        })
        
        # 如果沒有條件，返回空
        if not notion_filter["and"]:
            return {}
        
        return notion_filter
    
    def _convert_from_notion_page(self, page: Dict) -> Dict:
        """
        將Notion頁面轉換為標準數據格式
        
        Args:
            page: Notion頁面數據
            
        Returns:
            標準格式的數據字典
        """
        data = {
            "notion_page_id": page.get("id")
        }
        
        # 解析屬性
        properties = page.get("properties", {})
        
        for key, prop in properties.items():
            prop_type = prop.get("type")
            
            if prop_type == "title":
                title_array = prop.get("title", [])
                title_text = "".join([t.get("plain_text", "") for t in title_array])
                data[key] = title_text
            
            elif prop_type == "rich_text":
                text_array = prop.get("rich_text", [])
                rich_text = "".join([t.get("plain_text", "") for t in text_array])
                
                # 嘗試解析JSON
                try:
                    if rich_text.startswith("{") or rich_text.startswith("["):
                        json_data = json.loads(rich_text)
                        data[key] = json_data
                    else:
                        data[key] = rich_text
                except:
                    data[key] = rich_text
            
            elif prop_type == "number":
                data[key] = prop.get("number")
            
            elif prop_type == "select":
                select_obj = prop.get("select")
                if select_obj:
                    data[key] = select_obj.get("name")
            
            elif prop_type == "multi_select":
                multi_select = prop.get("multi_select", [])
                data[key] = [item.get("name") for item in multi_select]
            
            elif prop_type == "date":
                date_obj = prop.get("date")
                if date_obj:
                    start = date_obj.get("start")
                    end = date_obj.get("end")
                    
                    if end:
                        data[key] = {"start": start, "end": end}
                    else:
                        data[key] = start
            
            elif prop_type == "checkbox":
                data[key] = prop.get("checkbox")
            
            elif prop_type == "url":
                data[key] = prop.get("url")
            
            elif prop_type == "email":
                data[key] = prop.get("email")
            
            elif prop_type == "phone_number":
                data[key] = prop.get("phone_number")
            
            elif prop_type == "formula":
                formula = prop.get("formula", {})
                formula_type = formula.get("type")
                
                if formula_type:
                    data[key] = formula.get(formula_type)
            
            elif prop_type == "relation":
                relation = prop.get("relation", [])
                data[key] = [item.get("id") for item in relation]
            
            elif prop_type == "rollup":
                # 復雜的匯總字段，簡化處理
                rollup = prop.get("rollup", {})
                rollup_type = rollup.get("type")
                
                if rollup_type == "number":
                    data[key] = rollup.get("number")
                elif rollup_type == "date":
                    date_obj = rollup.get("date")
                    if date_obj:
                        data[key] = date_obj.get("start")
                elif rollup_type == "array":
                    # 簡化為字符串
                    data[key] = str(rollup.get("array"))
            
            # 其他類型保持原樣
        
        # 添加創建和修改時間
        data["created_time"] = page.get("created_time")
        data["last_edited_time"] = page.get("last_edited_time")
        
        return data
    
    def _match_filter(self, data: Dict, filter_query: Dict) -> bool:
        """
        檢查數據是否匹配過濾條件
        
        Args:
            data: 數據字典
            filter_query: 過濾條件
            
        Returns:
            是否匹配
        """
        for key, value in filter_query.items():
            # 如果字段不存在，不匹配
            if key not in data:
                return False
            
            # 根據值類型進行匹配
            if isinstance(value, (str, int, float, bool)):
                # 直接比較
                if data[key] != value:
                    return False
            
            elif isinstance(value, dict):
                # 處理運算符
                for op, op_value in value.items():
                    if op == "eq" and data[key] != op_value:
                        return False
                    elif op == "ne" and data[key] == op_value:
                        return False
                    elif op == "gt" and not (isinstance(data[key], (int, float)) and data[key] > op_value):
                        return False
                    elif op == "gte" and not (isinstance(data[key], (int, float)) and data[key] >= op_value):
                        return False
                    elif op == "lt" and not (isinstance(data[key], (int, float)) and data[key] < op_value):
                        return False
                    elif op == "lte" and not (isinstance(data[key], (int, float)) and data[key] <= op_value):
                        return False
                    elif op == "contains" and not (isinstance(data[key], str) and op_value in data[key]):
                        return False
            
            elif isinstance(value, list):
                # 檢查是否在列表中
                if data[key] not in value:
                    return False
        
        # 所有條件都匹配
        return True
    
    def export_data(self, collection: str = None, export_format: str = "json", filter_query: Dict = None, file_path: str = None) -> str:
        """
        導出數據
        
        Args:
            collection: 集合名稱，為None時使用默認值
            export_format: 導出格式，支持json, csv
            filter_query: 過濾條件
            file_path: 導出文件路徑，為None時自動生成
            
        Returns:
            導出文件路徑
        """
        # 獲取集合名稱
        if collection is None:
            collection = self.config.get("default_collection", "crawl_data")
        
        # 獲取數據
        data_list = self.get_data(collection, filter_query)
        
        if not data_list:
            self.logger.warning(f"沒有找到符合條件的數據: {collection}")
            return ""
        
        # 如果未指定路徑，自動生成
        if file_path is None:
            timestamp = int(time.time())
            export_dir = os.path.join(self.data_dir, "exports")
            os.makedirs(export_dir, exist_ok=True)
            file_path = os.path.join(export_dir, f"{collection}_{timestamp}.{export_format}")
        
        try:
            # 根據格式導出
            if export_format == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_list, f, indent=2, ensure_ascii=False)
            
            elif export_format == "csv":
                # 獲取所有字段
                all_fields = set()
                for data in data_list:
                    all_fields.update(data.keys())
                
                # 移除一些不需要的系統字段
                system_fields = {"notion_page_id"}
                fields = sorted(list(all_fields - system_fields))
                
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fields)
                    writer.writeheader()
                    
                    for data in data_list:
                        # 轉換複雜字段為字符串
                        row = {}
                        for field in fields:
                            value = data.get(field)
                            if isinstance(value, (dict, list)):
                                row[field] = json.dumps(value, ensure_ascii=False)
                            else:
                                row[field] = value
                        
                        writer.writerow(row)
            
            else:
                self.logger.error(f"不支持的導出格式: {export_format}")
                return ""
            
            self.logger.info(f"已導出 {len(data_list)} 條數據到: {file_path}")
            return file_path
        
        except Exception as e:
            self.logger.error(f"導出數據失敗: {str(e)}")
            return ""
    
    def create_schema(self, collection: str, schema: Dict) -> bool:
        """
        創建或更新集合的模式
        
        Args:
            collection: 集合名稱
            schema: 模式定義
            
        Returns:
            是否成功
        """
        # 對MongoDB應用模式
        if self.mongodb_enabled:
            try:
                # 獲取集合
                mongo_collection = self.mongodb_db[collection]
                
                # 創建索引
                indexes = schema.get("indexes", [])
                for index_def in indexes:
                    fields = index_def.get("fields", {})
                    options = index_def.get("options", {})
                    mongo_collection.create_index(fields, **options)
                
                # 設置驗證規則
                validation = schema.get("validation")
                if validation:
                    self.mongodb_db.command("collMod", collection, validator=validation)
                
                self.logger.info(f"已為MongoDB集合 {collection} 設置模式")
                return True
            
            except Exception as e:
                self.logger.error(f"為MongoDB集合設置模式失敗: {str(e)}")
                return False
        
        # 對Notion應用模式
        if self.notion_enabled:
            try:
                # 獲取數據庫ID
                database_id = self._get_notion_database_id(collection)
                
                if not database_id:
                    # 嘗試創建新數據庫
                    parent_page_id = self.notion_config.get("parent_page_id")
                    
                    if not parent_page_id:
                        self.logger.warning("未提供Notion父頁面ID，無法創建數據庫")
                        return False
                    
                    # 創建數據庫
                    properties = self._convert_schema_to_notion_properties(schema)
                    
                    response = self.notion_client.databases.create(
                        parent={"page_id": parent_page_id},
                        title=[{"type": "text", "text": {"content": collection}}],
                        properties=properties
                    )
                    
                    database_id = response["id"]
                    
                    # 更新配置
                    database_map = self.notion_config.get("database_map", {})
                    database_map[collection] = database_id
                    self.notion_config["database_map"] = database_map
                    
                    self.logger.info(f"已創建Notion數據庫: {collection}, ID: {database_id}")
                    return True
                
                else:
                    # 更新現有數據庫
                    properties = self._convert_schema_to_notion_properties(schema)
                    
                    self.notion_client.databases.update(
                        database_id=database_id,
                        properties=properties
                    )
                    
                    self.logger.info(f"已更新Notion數據庫模式: {collection}")
                    return True
            
            except Exception as e:
                self.logger.error(f"為Notion數據庫設置模式失敗: {str(e)}")
                return False
        
        return False
    
    def _convert_schema_to_notion_properties(self, schema: Dict) -> Dict:
        """
        將模式定義轉換為Notion屬性格式
        
        Args:
            schema: 模式定義
            
        Returns:
            Notion屬性定義
        """
        properties = {}
        fields = schema.get("fields", {})
        
        for field_name, field_def in fields.items():
            field_type = field_def.get("type", "text")
            
            if field_type == "string" or field_type == "text":
                properties[field_name] = {"rich_text": {}}
            elif field_type == "number" or field_type == "integer" or field_type == "float":
                properties[field_name] = {"number": {}}
            elif field_type == "boolean":
                properties[field_name] = {"checkbox": {}}
            elif field_type == "date":
                properties[field_name] = {"date": {}}
            elif field_type == "select":
                options = field_def.get("options", [])
                select_options = [{"name": opt} for opt in options]
                properties[field_name] = {"select": {"options": select_options}}
            elif field_type == "multi_select":
                options = field_def.get("options", [])
                select_options = [{"name": opt} for opt in options]
                properties[field_name] = {"multi_select": {"options": select_options}}
            elif field_type == "url":
                properties[field_name] = {"url": {}}
            elif field_type == "email":
                properties[field_name] = {"email": {}}
            elif field_type == "phone":
                properties[field_name] = {"phone_number": {}}
            elif field_type == "relation":
                related_db = field_def.get("database_id", "")
                properties[field_name] = {"relation": {"database_id": related_db}}
        
        # 確保至少有一個標題屬性
        if "title" not in properties and "name" not in properties:
            # 使用第一個字符串字段作為標題
            for field_name, field_def in fields.items():
                field_type = field_def.get("type", "text")
                if field_type == "string" or field_type == "text":
                    properties[field_name] = {"title": {}}
                    break
            
            # 如果仍然沒有標題，添加一個
            if "title" not in properties and "name" not in properties:
                properties["title"] = {"title": {}}
        
        return properties
    
    def delete_data(self, collection: str, filter_query: Dict) -> int:
        """
        刪除符合條件的數據
        
        Args:
            collection: 集合名稱
            filter_query: 過濾條件
            
        Returns:
            刪除的數據數量
        """
        deleted_count = 0
        
        # 從MongoDB刪除
        if self.mongodb_enabled:
            try:
                # 獲取集合
                mongo_collection = self.mongodb_db[collection]
                
                # 執行刪除
                result = mongo_collection.delete_many(filter_query)
                deleted_count += result.deleted_count
                
                self.logger.info(f"已從MongoDB刪除 {result.deleted_count} 條數據")
            except Exception as e:
                self.logger.error(f"從MongoDB刪除數據失敗: {str(e)}")
        
        # 從本地文件系統刪除
        if "local" in self.storage_modes:
            try:
                # 確定存儲路徑
                collection_dir = os.path.join(self.data_dir, collection)
                
                if os.path.exists(collection_dir):
                    # 獲取所有文件
                    local_deleted = 0
                    
                    for file_name in os.listdir(collection_dir):
                        if not file_name.endswith(".json"):
                            continue
                        
                        file_path = os.path.join(collection_dir, file_name)
                        
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            
                            # 應用過濾條件
                            if self._match_filter(data, filter_query):
                                os.remove(file_path)
                                local_deleted += 1
                        
                        except Exception as item_error:
                            self.logger.warning(f"處理本地數據項失敗 ({file_path}): {str(item_error)}")
                    
                    deleted_count += local_deleted
                    self.logger.info(f"已從本地刪除 {local_deleted} 條數據")
            
            except Exception as e:
                self.logger.error(f"從本地刪除數據失敗: {str(e)}")
        
        # 從Notion刪除
        if self.notion_enabled:
            try:
                # 獲取符合條件的頁面
                pages = self._get_from_notion(collection, filter_query)
                
                notion_deleted = 0
                
                # 刪除頁面（標記為歸檔）
                for page in pages:
                    page_id = page.get("notion_page_id")
                    
                    if page_id:
                        self.notion_client.pages.update(
                            page_id=page_id,
                            archived=True
                        )
                        notion_deleted += 1
                
                deleted_count += notion_deleted
                self.logger.info(f"已從Notion刪除 {notion_deleted} 條數據")
            
            except Exception as e:
                self.logger.error(f"從Notion刪除數據失敗: {str(e)}")
        
        return deleted_count
    
    def update_data(self, collection: str, filter_query: Dict, update_data: Dict) -> int:
        """
        更新符合條件的數據
        
        Args:
            collection: 集合名稱
            filter_query: 過濾條件
            update_data: 更新數據
            
        Returns:
            更新的數據數量
        """
        updated_count = 0
        
        # MongoDB更新
        if self.mongodb_enabled:
            try:
                # 獲取集合
                mongo_collection = self.mongodb_db[collection]
                
                # 執行更新
                result = mongo_collection.update_many(
                    filter_query,
                    {"$set": update_data}
                )
                
                updated_count += result.modified_count
                self.logger.info(f"已在MongoDB更新 {result.modified_count} 條數據")
            
            except Exception as e:
                self.logger.error(f"在MongoDB更新數據失敗: {str(e)}")
        
        # 本地文件系統更新
        if "local" in self.storage_modes:
            try:
                # 確定存儲路徑
                collection_dir = os.path.join(self.data_dir, collection)
                
                if os.path.exists(collection_dir):
                    # 獲取所有文件
                    local_updated = 0
                    
                    for file_name in os.listdir(collection_dir):
                        if not file_name.endswith(".json"):
                            continue
                        
                        file_path = os.path.join(collection_dir, file_name)
                        
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            
                            # 應用過濾條件
                            if self._match_filter(data, filter_query):
                                # 更新數據
                                data.update(update_data)
                                
                                # 重新保存
                                with open(file_path, "w", encoding="utf-8") as f:
                                    json.dump(data, f, indent=2, ensure_ascii=False)
                                
                                local_updated += 1
                        
                        except Exception as item_error:
                            self.logger.warning(f"處理本地數據項失敗 ({file_path}): {str(item_error)}")
                    
                    updated_count += local_updated
                    self.logger.info(f"已在本地更新 {local_updated} 條數據")
            
            except Exception as e:
                self.logger.error(f"在本地更新數據失敗: {str(e)}")
        
        # Notion更新
        if self.notion_enabled:
            try:
                # 獲取符合條件的頁面
                pages = self._get_from_notion(collection, filter_query)
                
                notion_updated = 0
                
                # 更新頁面
                for page in pages:
                    page_id = page.get("notion_page_id")
                    
                    if page_id:
                        # 轉換為Notion屬性
                        properties = self._convert_to_notion_properties(update_data)
                        
                        self.notion_client.pages.update(
                            page_id=page_id,
                            properties=properties
                        )
                        
                        notion_updated += 1
                
                updated_count += notion_updated
                self.logger.info(f"已在Notion更新 {notion_updated} 條數據")
            
            except Exception as e:
                self.logger.error(f"在Notion更新數據失敗: {str(e)}")
        
        return updated_count
    
    def count_data(self, collection: str, filter_query: Dict = None) -> int:
        """
        計算符合條件的數據數量
        
        Args:
            collection: 集合名稱
            filter_query: 過濾條件
            
        Returns:
            數據數量
        """
        # 優先從MongoDB獲取
        if self.mongodb_enabled:
            try:
                # 獲取集合
                mongo_collection = self.mongodb_db[collection]
                
                # 執行計數
                query = filter_query or {}
                count = mongo_collection.count_documents(query)
                
                self.logger.debug(f"MongoDB中符合條件的數據數量: {count}")
                return count
            
            except Exception as e:
                self.logger.error(f"在MongoDB計數失敗: {str(e)}")
        
        # 其他情況，獲取數據並計數
        data_list = self.get_data(collection, filter_query)
        return len(data_list)
    
    def aggregate_data(self, collection: str, pipeline: List[Dict]) -> List[Dict]:
        """
        執行聚合管道操作
        
        Args:
            collection: 集合名稱
            pipeline: 聚合管道
            
        Returns:
            聚合結果
        """
        # 僅支持MongoDB
        if self.mongodb_enabled:
            try:
                # 獲取集合
                mongo_collection = self.mongodb_db[collection]
                
                # 執行聚合
                results = list(mongo_collection.aggregate(pipeline))
                
                # 處理ObjectId
                for result in results:
                    if "_id" in result and hasattr(result["_id"], "__str__"):
                        result["_id"] = str(result["_id"])
                
                return results
            
            except Exception as e:
                self.logger.error(f"執行聚合管道失敗: {str(e)}")
        
        self.logger.warning("聚合操作僅支持MongoDB")
        return []
    
    def copy_data(self, source_collection: str, target_collection: str, filter_query: Dict = None) -> int:
        """
        複製數據
        
        Args:
            source_collection: 源集合名稱
            target_collection: 目標集合名稱
            filter_query: 過濾條件
            
        Returns:
            複製的數據數量
        """
        # 獲取源數據
        data_list = self.get_data(source_collection, filter_query)
        
        if not data_list:
            self.logger.warning(f"沒有找到符合條件的數據: {source_collection}")
            return 0
        
        # 批量保存到目標集合
        success = self.save_batch(data_list, target_collection)
        
        if success:
            self.logger.info(f"已複製 {len(data_list)} 條數據從 {source_collection} 到 {target_collection}")
            return len(data_list)
        else:
            self.logger.warning(f"複製數據失敗")
            return 0
    
    def __del__(self):
        """析構函數，確保資源正確關閉"""
        # 關閉MongoDB連接
        if self.mongodb_client:
            try:
                self.mongodb_client.close()
                self.logger.debug("已關閉MongoDB連接")
            except:
                pass                    # 應用過濾條件
                    if filter_query and not self._match_filter(data, filter_query):
                        continue
                    
                    data_list.append(data)
                    
                    # 檢查限制
                    if limit and len(data_list) >= limit:
                        break
                
                except Exception as item_error:
                    self.logger.warning(f"讀取本地數據項失敗 ({file_path}): {str(item_error)}")
            
            return data_list
        
        except Exception as e:
            self.logger.error(f"從本地獲取數據失敗: {str(e)}")
            return []
    
    def _save_to_mongodb(self, data: Dict, collection: str) -> bool:
        """
        保存數據到MongoDB
        
        Args:
            data: 數據字典
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        if not self.mongodb_enabled:
            return False
        
        try:
            # 獲取集合
            mongo_collection = self.mongodb_db[collection]
            
            # 檢查是否存在ID
            if "_id" in data:
                # 更新已有數據
                result = mongo_collection.update_one(
                    {"_id": data["_id"]},
                    {"$set": data},
                    upsert=True
                )
                success = result.acknowledged
            else:
                # 插入新數據
                result = mongo_collection.insert_one(data)
                success = result.acknowledged
            
            self.logger.debug(f"已保存數據到MongoDB: {collection}")
            return success
        
        except Exception as e:
            self.logger.error(f"保存數據到MongoDB失敗: {str(e)}")
            return False
    
    def _save_batch_to_mongodb(self, data_list: List[Dict], collection: str) -> bool:
        """
        批量保存數據到MongoDB
        
        Args:
            data_list: 數據字典列表
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        if not self.mongodb_enabled or not data_list:
            return False
        
        try:
            # 獲取集合
            mongo_collection = self.mongodb_db[collection]
            
            # 分離需要插入和更新的數據
            to_insert = []
            to_update = []
            
            for data in data_list:
                if "_id" in data:
                    to_update.append(data)
                else:
                    to_insert.append(data)
            
            # 批量插入
            if to_insert:
                insert_result = mongo_collection.insert_many(to_insert)
                insert_success = len(insert_result.inserted_ids) == len(to_insert)
            else:
                insert_success = True
            
            # 批量更新
            update_success = True
            for data in to_update:
                update_result = mongo_collection.update_one(
                    {"_id": data["_id"]},
                    {"$set": data},
                    upsert=True
                )
                if not update_result.acknowledged:
                    update_success = False
            
            self.logger.debug(
                f"已批量保存數據到MongoDB: {collection}, "
                f"插入: {len(to_insert)}, 更新: {len(to_update)}"
            )
            return insert_success and update_success
        
        except Exception as e:
            self.logger.error(f"批量保存數據到MongoDB失敗: {str(e)}")
            return False
    
    def _get_from_mongodb(self, collection: str, filter_query: Dict = None, limit: int = None) -> List[Dict]:
        """
        從MongoDB獲取數據
        
        Args:
            collection: 集合名稱
            filter_query: 過濾條件
            limit: 最大返回數量
            
        Returns:
            數據列表
        """
        if not self.mongodb_enabled:
            return []
        
        try:
            # 獲取集合
            mongo_collection = self.mongodb_db[collection]
            
            # 構建查詢條件
            query = filter_query or {}
            
            # 執行查詢
            cursor = mongo_collection.find(query)
            
            # 應用限制
            if limit:
                cursor = cursor.limit(limit)
            
            # 轉換為列表
            data_list = list(cursor)
            
            # 將ObjectId轉換為字符串
            for data in data_list:
                if "_id" in data and hasattr(data["_id"], "__str__"):
                    data["_id"] = str(data["_id"])
            
            return data_list
        
        except Exception as e:
            self.logger.error(f"從MongoDB獲取數據失敗: {str(e)}")
            return []
    
    def _save_to_notion(self, data: Dict, collection: str) -> bool:
        """
        保存數據到Notion
        
        Args:
            data: 數據字典
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        if not self.notion_enabled:
            return False
        
        try:
            # 獲取數據庫ID
            database_id = self._get_notion_database_id(collection)
            
            if not database_id:
                self.logger.warning(f"未找到Notion數據庫: {collection}")
                return False
            
            # 轉換數據格式為Notion屬性
            properties = self._convert_to_notion_properties(data)
            
            # 檢查是否已存在頁面ID
            page_id = data.get("notion_page_id")
            
            if page_id:
                # 更新已有頁面
                self.notion_client.pages.update(
                    page_id=page_id,
                    properties=properties
                )
            else:
                # 創建新頁面
                response = self.notion_client.pages.create(
                    parent={"database_id": database_id},
                    properties=properties
                )
                page_id = response["id"]
            
            self.logger.debug(f"已保存數據到Notion: {collection}, 頁面ID: {page_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存數據到Notion失敗: {str(e)}")
            return False
    
    def _save_batch_to_notion(self, data_list: List[Dict], collection: str) -> bool:
        """
        批量保存數據到Notion
        
        Args:
            data_list: 數據字典列表
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        if not self.notion_enabled or not data_list:
            return False
        
        try:
            # 獲取數據庫ID
            database_id = self._get_notion_database_id(collection)
            
            if not database_id:
                self.logger.warning(f"未找到Notion數據庫: {collection}")
                return False
            
            # 逐個保存，Notion API不支持批量操作
            success_count = 0
            
            for data in data_list:
                try:
                    # 轉換數據格式為Notion屬性
                    properties = self._convert_to_notion_properties(data)
                    
                    # 檢查是否已存在頁面ID
                    page_id = data.get("notion_page_id")
                    
                    if page_id:
                        # 更新已有頁面
                        self.notion_client.pages.update(
                            page_id=page_id,
                            properties=properties
                        )
                    else:
                        # 創建新頁面
                        self.notion_client.pages.create(
                            parent={"database_id": database_id},
                            properties=properties
                        )
                    
                    success_count += 1
                except Exception as item_error:
                    self.logger.warning(f"保存單個數據項到Notion失敗: {str(item_error)}")
            
            self.logger.debug(f"已批量保存 {success_count}/{len(data_list)} 項數據到Notion")
            return success_count == len(data_list)
        
        except Exception as e:
            self.logger.error(f"批量保存數據到Notion失敗: {str(e)}")
            return False
    
    def _get_from_notion(self, collection: str, filter_query: Dict = None, limit: int = None) -> List[Dict]:
        """
        從Notion獲取數據
        
        Args:
            collection: 集合名稱
            filter_query: 過濾條件
            limit: 最大返回數量
            
        Returns:
            數據列表
        """
        if not self.notion_enabled:
            return []
        
        try:
            # 獲取數據庫ID
            database_id = self._get_notion_database_id(collection)
            
            if not database_id:
                self.logger.warning(f"未找到Notion數據庫: {collection}")
                return []
            
            # 構建查詢參數
            query_params = {
                "database_id": database_id
            }
            
            # 轉換過濾條件為Notion格式
            if filter_query:
                notion_filter = self._convert_to_notion_filter(filter_query)
                if notion_filter:
                    query_params["filter"] = notion_filter
            
            # 應用限制
            if limit:
                query_params["page_size"] = min(limit, 100)  # Notion API限制最大為100
            
            # 執行查詢
            response = self.notion_client.databases.query(**query_params)
            
            # 提取頁面列表
            pages = response.get("results", [])
            
            # 獲取更多結果（如果需要）
            while response.get("has_more") and (not limit or len(pages) < limit):
                query_params["start_cursor"] = response.get("next_cursor")
                response = self.notion_client.databases.query(**query_params)
                pages.extend(response.get("results", []))
                
                if limit and len(pages) >= limit:
                    pages = pages[:limit]
                    break
            
            # 轉換為標準格式
            data_list = []
            for page in pages:
                data = self._convert_from_notion_page(page)
                data_list.append(data)
            
            return data_list
        
        except Exception as e:
            self.logger.error(f"從Notion獲取數據失敗: {str(e)}")
            return []
    
    def _get_notion_database_id(self, collection: str) -> str:
        """
        獲取Notion數據庫ID
        
        Args:
            collection: 集合名稱
            
        Returns:
            數據庫ID或空字符串
        """
        # 從配置中查找
        database_map = self.notion_config.get("database_map", {})
        if collection in database_map:
            return database_map[collection]
        
        # 如果未找到，嘗試搜索
        try:
            response = self.notion_client.search(
                query=collection,
                filter={"property": "object", "value": "database"}
            )
            
            for result in response.get("results", []):
                if result.get("object") == "database":
                    title = result.get("title", [])
                    db_title = "".join([t.get("plain_text", "") for t in title])
                    
                    if db_title.lower() == collection.lower():
                        db_id = result.get("id")
                        # 更新配置
                        database_map[collection] = db_id
                        return db_id
            
            return ""
        
        except Exception as e:
            self.logger.error(f"搜索Notion數據庫失敗: {str(e)}")
            return ""
    
    def _convert_to_notion_properties(self, data: Dict) -> Dict:
        """
        將數據轉換為Notion屬性格式
        
        Args:
            data: 數據字典
            
        Returns:
            Notion屬性字典
        """
        properties = {}
        
        for key, value in data.items():
            if key in ["notion_page_id", "parent", "id", "created_time", "last_edited_time", "url", "archived"]:
                continue
            
            # 根據值類型設置屬性
            if isinstance(value, str):
                properties[key] = {"rich_text": [{"text": {"content": value}}]}
            elif isinstance(value, int):
                properties[key] = {"number": value}
            elif isinstance(value, float):
                properties[key] = {"number": value}
            elif isinstance(value, bool):
                properties[key] = {"checkbox": value}
            elif isinstance(value, list):
                # 處理多選項或關聯
                if all(isinstance(item, str) for item in value):
                    properties[key] = {"multi_select": [{"name": item} for item in value]}
                else:
                    # 如果不是字符串列表，轉為JSON字符串
                    json_value = json.dumps(value)
                    properties[key] = {"rich_text": [{"text": {"content": json_value}}]}
            elif isinstance(value, dict):
                # 如果是字典，轉為JSON字符串
                json_value = json.dumps(value)
                properties[key] = {"rich_text": [{"text": {"content": json_value}}]}
            elif value is None:
                # 忽略空值
                continue
            else:
                # 其他類型轉為字符串
                properties[key] = {"rich_text": [{"text": {"content": str(value)}}]}
        
        # 確保至少有一個標題屬性
        if "title" not in properties and "name" not in properties:
            # 使用ID或時間戳作為標題
            title_value = data.get("id") or data.get("_id") or str(int(time.time()))
            properties["title"] = {"title": [{"text": {"content": str(title_value)}}]}
        
        return properties
    
    def _convert_to_notion_filter(self, filter_query: Dict) -> Dict:
        """
        將過濾條件轉換為Notion查詢格式
        
        Args:
            filter_query: 過濾條件字典
            
        Returns:
            Notion過濾條件字典
        """
        # 簡單實現，只支持基本條件
        notion_filter = {"and": []}
        
        for key, value in filter_query.items():
            if isinstance(value#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import logging
import csv
from typing import Dict, List, Optional, Any, Union

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception
from ..utils.config_loader import ConfigLoader


class DataPersistenceManager:
    """
    數據持久化管理器，負責數據的保存、載入和管理。
    支持本地文件系統、MongoDB、Notion等多種存儲方式。
    """
    
    def __init__(
        self,
        config: Dict = None,
        log_level: int = logging.INFO
    ):
        """
        初始化數據持久化管理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.config = config or {}
        
        # 存儲設置
        self.storage_modes = self.config.get("storage_modes", ["local"])
        
        # 本地存儲設置
        self.local_config = self.config.get("local_config", {})
        self.data_dir = self.local_config.get("data_dir", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # MongoDB設置
        self.mongodb_config = self.config.get("mongodb_config", {})
        self.mongodb_enabled = self.mongodb_config.get("enabled", False) and "mongodb" in self.storage_modes
        self.mongodb_client = None
        self.mongodb_db = None
        
        # Notion設置
        self.notion_config = self.config.get("notion_config", {})
        self.notion_enabled = self.notion_config.get("enabled", False) and "notion" in self.storage_modes
        self.notion_client = None
        
        # 字段映射
        self.field_mappings = self.config.get("field_mappings", {})
        
        # 初始化存儲驅動
        self._init_storage_drivers()
        
        self.logger.info("數據持久化管理器初始化完成")
    
    def _init_storage_drivers(self):
        """初始化存儲驅動"""
        # 初始化MongoDB
        if self.mongodb_enabled:
            self._init_mongodb()
        
        # 初始化Notion
        if self.notion_enabled:
            self._init_notion()
    
    def _init_mongodb(self):
        """初始化MongoDB連接"""
        try:
            import pymongo
            
            # 連接參數
            host = self.mongodb_config.get("host", "localhost")
            port = self.mongodb_config.get("port", 27017)
            username = self.mongodb_config.get("username")
            password = self.mongodb_config.get("password")
            auth_source = self.mongodb_config.get("auth_source", "admin")
            db_name = self.mongodb_config.get("db_name", "crawler")
            
            # 構建連接字符串
            connection_string = f"mongodb://"
            
            if username and password:
                connection_string += f"{username}:{password}@"
            
            connection_string += f"{host}:{port}/{db_name}"
            
            if username and password:
                connection_string += f"?authSource={auth_source}"
            
            # 連接MongoDB
            self.mongodb_client = pymongo.MongoClient(connection_string)
            self.mongodb_db = self.mongodb_client[db_name]
            
            # 測試連接
            self.mongodb_client.admin.command('ping')
            
            self.logger.info(f"已連接MongoDB: {host}:{port}/{db_name}")
        
        except ImportError:
            self.logger.warning("未安裝pymongo庫，無法使用MongoDB存儲")
            self.mongodb_enabled = False
        
        except Exception as e:
            self.logger.error(f"連接MongoDB失敗: {str(e)}")
            self.mongodb_enabled = False
    
    def _init_notion(self):
        """初始化Notion連接"""
        try:
            from notion_client import Client
            
            # API設置
            token = self.notion_config.get("token")
            
            if not token:
                self.logger.warning("未提供Notion API令牌，無法使用Notion存儲")
                self.notion_enabled = False
                return
            
            # 初始化Notion客戶端
            self.notion_client = Client(auth=token)
            
            # 測試連接
            self.notion_client.users.me()
            
            self.logger.info("已連接Notion API")
        
        except ImportError:
            self.logger.warning("未安裝notion_client庫，無法使用Notion存儲")
            self.notion_enabled = False
        
        except Exception as e:
            self.logger.error(f"連接Notion API失敗: {str(e)}")
            self.notion_enabled = False
    
    def save_data(self, data: Dict, collection: str = None) -> bool:
        """
        保存數據
        
        Args:
            data: 數據字典
            collection: 集合名稱，為None時使用默認值
            
        Returns:
            是否成功保存
        """
        # 獲取集合名稱
        if collection is None:
            collection = self.config.get("default_collection", "crawl_data")
        
        # 添加時間戳
        if "timestamp" not in data:
            data["timestamp"] = int(time.time())
        
        # 應用字段映射
        mapped_data = self._apply_field_mapping(data)
        
        success = True
        
        # 保存到本地
        if "local" in self.storage_modes:
            local_result = self._save_to_local(mapped_data, collection)
            success = success and local_result
        
        # 保存到MongoDB
        if self.mongodb_enabled:
            mongodb_result = self._save_to_mongodb(mapped_data, collection)
            success = success and mongodb_result
        
        # 保存到Notion
        if self.notion_enabled:
            notion_result = self._save_to_notion(mapped_data, collection)
            success = success and notion_result
        
        return success
    
    def save_batch(self, data_list: List[Dict], collection: str = None) -> bool:
        """
        批量保存數據
        
        Args:
            data_list: 數據字典列表
            collection: 集合名稱，為None時使用默認值
            
        Returns:
            是否成功保存
        """
        # 獲取集合名稱
        if collection is None:
            collection = self.config.get("default_collection", "crawl_data")
        
        # 添加時間戳並應用字段映射
        timestamp = int(time.time())
        mapped_data_list = []
        
        for data in data_list:
            if "timestamp" not in data:
                data["timestamp"] = timestamp
            
            mapped_data = self._apply_field_mapping(data)
            mapped_data_list.append(mapped_data)
        
        success = True
        
        # 保存到本地
        if "local" in self.storage_modes:
            local_result = self._save_batch_to_local(mapped_data_list, collection)
            success = success and local_result
        
        # 保存到MongoDB
        if self.mongodb_enabled:
            mongodb_result = self._save_batch_to_mongodb(mapped_data_list, collection)
            success = success and mongodb_result
        
        # 保存到Notion
        if self.notion_enabled:
            notion_result = self._save_batch_to_notion(mapped_data_list, collection)
            success = success and notion_result
        
        return success
    
    def get_data(self, collection: str = None, filter_query: Dict = None, limit: int = None) -> List[Dict]:
        """
        獲取數據
        
        Args:
            collection: 集合名稱，為None時使用默認值
            filter_query: 過濾條件
            limit: 最大返回數量
            
        Returns:
            數據列表
        """
        # 獲取集合名稱
        if collection is None:
            collection = self.config.get("default_collection", "crawl_data")
        
        # 優先從MongoDB獲取
        if self.mongodb_enabled:
            try:
                return self._get_from_mongodb(collection, filter_query, limit)
            except Exception as e:
                self.logger.error(f"從MongoDB獲取數據失敗: {str(e)}")
        
        # 從本地獲取
        if "local" in self.storage_modes:
            try:
                return self._get_from_local(collection, filter_query, limit)
            except Exception as e:
                self.logger.error(f"從本地獲取數據失敗: {str(e)}")
        
        # 從Notion獲取
        if self.notion_enabled:
            try:
                return self._get_from_notion(collection, filter_query, limit)
            except Exception as e:
                self.logger.error(f"從Notion獲取數據失敗: {str(e)}")
        
        return []
    
    def _apply_field_mapping(self, data: Dict) -> Dict:
        """
        應用字段映射
        
        Args:
            data: 原始數據字典
            
        Returns:
            映射後的數據字典
        """
        if not self.field_mappings:
            return data
        
        mapped_data = {}
        
        # 處理映射字段
        for src_field, dst_field in self.field_mappings.items():
            if src_field in data:
                # 如果目標字段是嵌套的，創建嵌套結構
                if "." in dst_field:
                    parts = dst_field.split(".")
                    current = mapped_data
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            current[part] = data[src_field]
                        else:
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                else:
                    mapped_data[dst_field] = data[src_field]
        
        # 處理未映射字段
        for field, value in data.items():
            if field not in self.field_mappings:
                mapped_data[field] = value
        
        return mapped_data
    
    def _save_to_local(self, data: Dict, collection: str) -> bool:
        """
        保存數據到本地文件系統
        
        Args:
            data: 數據字典
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        try:
            # 確定存儲路徑
            collection_dir = os.path.join(self.data_dir, collection)
            os.makedirs(collection_dir, exist_ok=True)
            
            # 生成文件名
            file_id = data.get("id", str(int(time.time() * 1000)))
            file_path = os.path.join(collection_dir, f"{file_id}.json")
            
            # 保存數據
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"已保存數據到本地: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存數據到本地失敗: {str(e)}")
            return False
    
    def _save_batch_to_local(self, data_list: List[Dict], collection: str) -> bool:
        """
        批量保存數據到本地文件系統
        
        Args:
            data_list: 數據字典列表
            collection: 集合名稱
            
        Returns:
            是否成功保存
        """
        try:
            # 確定存儲路徑
            collection_dir = os.path.join(self.data_dir, collection)
            os.makedirs(collection_dir, exist_ok=True)
            
            # 批量存儲文件
            success_count = 0
            
            for data in data_list:
                try:
                    # 生成文件名
                    file_id = data.get("id", str(int(time.time() * 1000) + success_count))
                    file_path = os.path.join(collection_dir, f"{file_id}.json")
                    
                    # 保存數據
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    success_count += 1
                except Exception as item_error:
                    self.logger.warning(f"保存單個數據項到本地失敗: {str(item_error)}")
            
            self.logger.debug(f"已批量保存 {success_count}/{len(data_list)} 項數據到本地")
            return success_count == len(data_list)
        
        except Exception as e:
            self.logger.error(f"批量保存數據到本地失敗: {str(e)}")
            return False
    
    def _get_from_local(self, collection: str, filter_query: Dict = None, limit: int = None) -> List[Dict]:
        """
        從本地文件系統獲取數據
        
        Args:
            collection: 集合名稱
            filter_query: 過濾條件
            limit: 最大返回數量
            
        Returns:
            數據列表
        """
        try:
            # 確定存儲路徑
            collection_dir = os.path.join(self.data_dir, collection)
            
            if not os.path.exists(collection_dir):
                return []
            
            # 讀取數據
            data_list = []
            
            for file_name in os.listdir(collection_dir):
                if not file_name.endswith(".json"):
                    continue
                
                file_path = os.path.join(collection_dir, file_name)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # 應用過濾條件
                    if filter_query and not self._match_filter(data, filter_query):
                        continue
                    
                    data_list.append(data)