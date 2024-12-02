from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
from botocore.exceptions import ClientError
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DynamoDB Configuration
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Employees')

# Home Page
@app.route('/')
def index():
    try:
        response = table.scan()
        employees = response.get('Items', [])
        return render_template('index.html', employees=employees)
    except ClientError as e:
        flash(f"Error fetching data: {e.response['Error']['Message']}", "danger")
        return render_template('index.html', employees=[])

# Add Employee
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']

        try:
            table.put_item(Item={
                'employee_id': str(uuid.uuid4()),
                'name': name,
                'email': email,
                'department': department
            })
            flash("Employee added successfully!", "success")
            return redirect(url_for('index'))
        except ClientError as e:
            flash(f"Error adding employee: {e.response['Error']['Message']}", "danger")
    return render_template('add_employee.html')

# Update Employee
@app.route('/update/<employee_id>', methods=['GET', 'POST'])
def update_employee(employee_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']

        try:
            table.update_item(
                Key={'employee_id': employee_id},
                UpdateExpression="SET #n=:name, email=:email, department=:department",
                ExpressionAttributeNames={'#n': 'name'},
                ExpressionAttributeValues={
                    ':name': name,
                    ':email': email,
                    ':department': department
                }
            )
            flash("Employee updated successfully!", "success")
            return redirect(url_for('index'))
        except ClientError as e:
            flash(f"Error updating employee: {e.response['Error']['Message']}", "danger")

    try:
        response = table.get_item(Key={'employee_id': employee_id})
        employee = response.get('Item')
        return render_template('update_employee.html', employee=employee)
    except ClientError as e:
        flash(f"Error fetching employee: {e.response['Error']['Message']}", "danger")
        return redirect(url_for('index'))

# Delete Employee
@app.route('/delete/<employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        table.delete_item(Key={'employee_id': employee_id})
        flash("Employee deleted successfully!", "success")
    except ClientError as e:
        flash(f"Error deleting employee: {e.response['Error']['Message']}", "danger")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
