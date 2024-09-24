from flask import (
    Blueprint, flash, g, render_template, request, session, url_for, redirect
)
from werkzeug.exceptions import abort
from todo.auth import loginRequired
from todo.db import getDb

bp=Blueprint('todo', __name__)
@bp.route('/')
@loginRequired
def index():
    db, c = getDb()
    c.execute(
        'SELECT t.id, t.description, u.username, t.completed, t.created_at '
        'FROM todo t JOIN user u ON t.created_by = u.id '
        'WHERE t.created_by = %s '
        'ORDER BY t.created_at DESC'
        , (g.user['id'],)
    )
    todos = c.fetchall()
    return render_template('todo/index.html', todos=todos)

@bp.route('/create', methods=['GET', 'POST'])
@loginRequired
def create():
    if request.method == 'POST':
        description = request.form['description']
        error = None
        if not description:
            error = 'Description is required.'
        if error is not None:
            flash(error)
        else:
            db, c = getDb()
            c.execute(
                'INSERT INTO todo (description, completed, created_by)'
                ' VALUES (%s, %s, %s)',
                (description, False, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))
        
    return render_template('todo/create.html')


def getTodoById(id):
    db, c = getDb()
    c.execute(
        'SELECT t.id, t.description, t.completed, t.created_at, u.username'
        ' FROM todo t JOIN user u ON t.created_by = u.id WHERE t.id = %s',
        (id,)
    )
    todo = c.fetchone()
    if todo is None:
        abort(404, f"Todo id {0} doesn't exist.".format(id))
    return todo

@bp.route('/<int:id>/update', methods=['GET','POST'])
@loginRequired
def update(id):
    todo = getTodoById(id)
    if request.method == 'POST':
        description = request.form['description']
        completed = True if request.form.get('completed') == 'on' else False
        error = None
        if not description:
            error = 'Description is required.'
        if error is not None:
            flash(error)
        else:
            db, c = getDb()
            c.execute(
                'UPDATE todo SET description = %s, completed = %s'
                ' WHERE id = %s and created_by = %s',
                (description, completed, id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('todo.index'))
    return render_template('todo/update.html', todo=todo)

@bp.route('/<int:id>/delete', methods=['POST'])
@loginRequired
def delete(id):
    db, c = getDb()
    c.execute('DELETE FROM todo WHERE id = %s and created_by= %s', (id, g.user['id']))
    db.commit()
    return redirect(url_for('todo.index'))