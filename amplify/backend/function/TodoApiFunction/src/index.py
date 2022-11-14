import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from aws_lambda_powertools import Logger
from pydantic import BaseModel
import boto3
import uuid

# 環境変数取得
ENV = os.environ['ENV']
STORAGE_TODODB_NAME = os.environ.get("STORAGE_TODODB_NAME")

# boto3 初期化
ddb = boto3.resource("dynamodb")
table = ddb.Table(STORAGE_TODODB_NAME)

## FastAPI 初期化
app = FastAPI(
    title="TodoAPI",
    root_path=f"/{ENV}",
    openapi_url="/openapi.json"
)

# ロガー初期化
app.logger = Logger(level="INFO", service=__name__)

# CORS設定
allow_origins = ['http://localhost:8080']
if 'ALLOW_ORIGIN' in os.environ.keys():
    allow_origins.append(os.environ['ALLOW_ORIGIN'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# スキーマ設定
class RequestTodo(BaseModel):
    """
    リクエストスキーマ
    """
    name: str
    description: str

class ResponseTodo(BaseModel):
    """
    レスポンススキーマ
    """
    id: str
    name: str
    description: str


@app.get("/todos")
def get_todos_list():
    """
    Todo 一覧を取得する
    """
    # TODO 一覧取得処理を書く
    return {
        "id": "1",
        "name": "todo-1",
        "description": "hogehogehoge"
    }

@app.get("/todos/{id}")
def get_todo_item(id: str):
    """
    Todo アイテムを取得する
    """
    key = {
        "id": id
    }

    response = table.get_item(Key=key)

    return ResponseTodo.parse_obj(response["Item"])

@app.post("/todos", response_model=ResponseTodo)
def post_todo_item(todo_in: RequestTodo):
    """
    Todo アイテムを取得する
    """
    id = str(uuid.uuid4())
    create_item = todo_in.dict()
    create_item["id"] = id

    result = table.put_item(Item=create_item)
    app.logger.info(result)

    return ResponseTodo.parse_obj(create_item)

@app.put("/todos/{id}", response_model=ResponseTodo)
def update_todo_item(id: str):
    """
    Todo アイテムを更新する
    """
    # TODO アップデート処理
    return {
        "id": id,
        "name": "todo-1",
        "description": "hogehogehoge"
    }

@app.delete("/todos/{id}")
def delete_todo_item(id: str):
    """
    Todo アイテムを削除する
    """
    # TODO 削除処理
    return {
        "id": id,
        "name": "todo-1",
        "description": "hogehogehoge"
    }


handler = Mangum(app)