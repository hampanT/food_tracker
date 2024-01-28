from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
#databasen initaliseras med inställningarna från vår app
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from alembic import op
import sqlalchemy as sa

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    datepicker = db.Column(db.DateTime, nullable=True)
    purchase_date = db.Column(db.DateTime, default=datetime.today) #snubben i guiden körde med utcnow. 
                                                                #DVS utcnow utgår tiden från london medan datetime.now går på användarens lokala tid
with app.app_context():
    db.create_all()

    def __repr__(self):
        return '<Task %r>' % self.id

def get_objects(sort_order='latest'):
    if sort_order == 'latest':
        return Todo.query.order_by(Todo.datepicker).all()
    return Todo.query.all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        expiration_str = request.form.get("datepicker")

        if not task_content:
            error_message = "Du måste ange ett värde för både uppgift och datum."
            sort_order = request.args.get('sort', 'latest')
            return render_template('index.html', error_message=error_message, tasks=get_objects(sort_order))

        # Check if expiration_str is not empty before parsing
        if expiration_str:
            try:
                expiration = datetime.strptime(expiration_str, '%d/%m/%Y')
            except ValueError:
                error_message = "Invalid date format, snälla använd DD/MM/YYYY :)"
                return render_template('index.html', error_message=error_message, tasks=get_objects(sort_order))
        else:
            expiration = None  # Set expiration to None if the datepicker is empty

        new_task = Todo(content=task_content, datepicker=expiration)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f"Error adding task: {e}")
            return f'There was an issue adding the task: {e}'

    else:
        sort_order = request.args.get('sort', 'latest')
        tasks = get_objects(sort_order)
        return render_template('/index.html', tasks=tasks, error_message=None)
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        error_message = "Du måste ange ett värde"
        return error_message
    

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']


        try:
            db.session.commit()
            return redirect('/') #('/') detta innebär en redirect tillbaka till homepage
        except:
            error_message = "Du måste ange ett värde"
            return error_message
        
    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)
