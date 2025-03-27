from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SqlDbTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_uri = tool_parameters.get("db_uri") or self.runtime.credentials.get("db_uri")
        sql_query = tool_parameters.get("sql_query").strip()

        try:
            # 创建数据库引擎
            engine = create_engine(db_uri)
            
            # 创建连接并执行查询
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
                
                # 获取列名
                columns = result.keys()
                
                # 获取所有结果行
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                
                yield self.create_json_message({
                    "columns": list(columns),
                    "rows": rows
                })
                
        except SQLAlchemyError as e:
            yield ValueError(f"SQLAlchemyError: {e}")
