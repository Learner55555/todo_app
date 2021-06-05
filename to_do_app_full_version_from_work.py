from flask import Flask, render_template, request, redirect, url_for,jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

from sqlalchemy.orm import backref

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:235689@localhost:5432/todoapp3_migrate'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app, session_options={"expire_on_commit": False})
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__='todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable = False)
    completed = db.Column(db.Boolean, nullable = False, default = False)
    parent_todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=True)
    
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__='todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = False)
    children_todos = db.relationship('Todo', backref='parent_todolist', lazy = True)

# db.create_all()

@app.route('/todos/create', methods = ['POST'])
def create_todo():
    error = False 
    dictionary_variable = {}       
    try:
        variable_from_html = request.get_json()['description'] # dictionary['description]
        list_id = request.get_json()['parent_todolist_id']
        todo = Todo(description = variable_from_html, completed =False, parent_todolist_id = list_id)
        db.session.add(todo)
        db.session.commit()
        dictionary_variable['id'] = todo.id
        dictionary_variable['description'] = todo.description
        dictionary_variable['completed'] = todo.completed
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(dictionary_variable)

@app.route('/todos/<todo_id>/set-completed', methods= ['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo= Todo.query.get(todo_id)
        db.session.delete(todo)
        # Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index_page.html',
    lists=TodoList.query.all(),
    active_list=TodoList.query.get(list_id),
    todos=Todo.query.filter_by(parent_todolist_id=list_id).order_by('id').all())

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id = 1))
