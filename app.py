from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# 1. FlaskアプリケーションとDBの設定
app = Flask(__name__)
# SQLiteデータベースファイル'tasks.db'を使用
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
# 変更トラッキングの警告を非表示にする
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyインスタンスの作成
db = SQLAlchemy(app)

# 2. データベースモデル（テーブル構造）の定義
# Taskクラスがデータベースの'task'テーブルに対応します
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        # オブジェクトがprintされたときに表示される内容
        return f'<Task {self.id}: {self.title}>'

    # APIレスポンス用の辞書形式に変換するメソッド
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed
        }

# 3. データベースの初期化
# アプリケーションコンテキスト内でテーブルを作成します
with app.app_context():
    db.create_all()

# 4. APIエンドポイント（ルート）の定義

# 全タスクの取得 (GET) および 新しいタスクの作成 (POST)
@app.route('/tasks', methods=['GET', 'POST'])
def handle_tasks():
    if request.method == 'POST':
        # POSTリクエスト: 新しいタスクを作成
        data = request.get_json()
        if 'title' not in data:
            return jsonify({'error': 'Missing title'}), 400
        
        new_task = Task(title=data['title'])
        
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify(new_task.to_dict()), 201

    # GETリクエスト: 全タスクを取得
    tasks = Task.query.all()
    # 取得した全タスクを辞書のリストに変換
    tasks_list = [task.to_dict() for task in tasks]
    return jsonify(tasks_list)

# 特定タスクの取得 (GET)、更新 (PUT)、削除 (DELETE)
@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_task(task_id):
    # プライマリキー（id）でタスクを検索
    task = Task.query.get_or_404(task_id)

    if request.method == 'GET':
        # GETリクエスト: 特定のタスクを取得
        return jsonify(task.to_dict())

    elif request.method == 'PUT':
        # PUTリクエスト: 特定のタスクを更新
        data = request.get_json()
        
        if 'title' in data:
            task.title = data['title']
        if 'completed' in data:
            task.completed = data['completed']
        
        db.session.commit()
        return jsonify(task.to_dict())

    elif request.method == 'DELETE':
        # DELETEリクエスト: 特定のタスクを削除
        db.session.delete(task)
        db.session.commit()
        # 成功を示す空のレスポンス
        return jsonify({}), 204

if __name__ == '__main__':
    app.run(debug=True)