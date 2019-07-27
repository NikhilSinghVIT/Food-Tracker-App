from flask import Flask,render_template,g,request
import sqlite3
from datetime import datetime


app = Flask(__name__)

def connect_db():
	sql = sqlite3.connect('C:/Users/NIKHIL/Desktop/food_tracker/food_log.db')
	sql.row_factory = sqlite3.Row
	return sql


def get_db():
	if not hasattr(g,'sqlite3'):
		g.sqlite_db = connect_db()
	return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
	if hasattr(g,'sqlite3'):
		g.sqlite_db.close()



@app.route('/',methods=['POST','GET'])
def index():
	db = get_db()
	if request.method == 'POST':
		date = request.form['date']
		dt = datetime.strptime(date,'%Y-%m-%d')
		database_date = datetime.strftime(dt,'%Y%m%d')

		cur = db.execute('select * from log_date where entry_date = ?', [database_date])
		nx_res = cur.fetchall()

		if len(nx_res) == 0:
			db.execute('insert into log_date (entry_date) values(?)',[database_date])
		
		cur = db.execute('select * from log_date where id = (select MAX(id) from log_date)')
		res = cur.fetchall()
		print(res[0])
		db.execute('insert into food_date values(?,?)', [0, res[0]['id']])
		db.commit()
	cur = db.execute('''select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories 
                        from log_date 
                        join food_date on food_date.log_date_id = log_date.id 
                        join food on food.id = food_date.food_id 
                        group by log_date.id order by log_date.entry_date desc''')
	#cur = db.execute('select entry_date from log_date order by entry_date desc')

	results = cur.fetchall()
	date_results = []

	for i in results:
		single_date = {}
		single_date['entry_date'] = i['entry_date']
		single_date['protein'] = i['protein']
		single_date['carbohydrates'] = i['carbohydrates']
		single_date['fat'] = i['fat']
		single_date['calories'] = i['calories']

		d = datetime.strptime(str(i['entry_date']),'%Y%m%d')
		single_date['pretty_date'] =  datetime.strftime(d, '%B %d, %Y')
		date_results.append(single_date)

	return render_template('home.html',results=date_results)

@app.route('/view/<date>',methods=['GET','POST'])
def view(date):
	print("debug--", date)
	db = get_db()
	cur = db.execute('select id,entry_date from log_date where entry_date = ' + date)
	date_result = cur.fetchone()

	if request.method == 'POST':
		db.execute('insert into food_date (food_id,log_date_id) values (?,?)',[request.form['food-select'],date_result['id']])
		db.commit()
		


	
	d = datetime.strptime(str(date_result['entry_date']),'%Y%m%d')
	pretty_date = datetime.strftime(d,'%B %d,%Y')

	food_cur = db.execute('select id,name from food where id > 0')
	food_result = food_cur.fetchall()
	log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ? and food.id > 0', [date])
	log_results = log_cur.fetchall()
	

	totals = {}
	totals['protein'] = 0
	totals['carbohydrates'] = 0
	totals['fat'] = 0
	totals['calories'] = 0

	for food in log_results:
		totals['protein'] += food['protein']
		totals['carbohydrates'] += food['carbohydrates']
		totals['fat'] += food['fat']
		totals['calories'] += food['calories']

	return render_template('day.html',entry_date= date_result['entry_date'],pretty_date = pretty_date,food_result = food_result,log_results=log_results,totals=totals)

@app.route('/add_food',methods=['GET','POST'])
def add_food():
	db = get_db()
	if request.method == 'POST':
		food_name = request.form['food-name']
		protein = int(request.form['protein'])
		carbs = int(request.form['carbohydrates'])
		fat = int(request.form['fat'])
		calories = protein*4+carbs*4+fat*9

		db.execute('insert into food (name,protein,carbohydrates,fat,calories) values(?,?,?,?,?)',[food_name,protein,carbs,fat,calories])
		db.commit()
	cur = db.execute('select name,protein,carbohydrates,fat,calories from food where id > 0')
	results = cur.fetchall()

	return render_template('add_food.html',results=results)
    

if __name__ == '__main__':
 	app.run(debug=True)