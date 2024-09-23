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
        'SELECT t.id, t.description, u.username, t.completed, t.created_at FROM todo t JOIN user u ON t.created_by = u.id ORDER BY t.created_at DESC'
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

@bp.route('/<int:id>/update', methods=['GET','POST'])
@loginRequired
def update():
    return render_template('todo/update.html')