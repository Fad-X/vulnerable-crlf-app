from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
from lxml import etree  # Import lxml for XML parsing with DTD/XXE support
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = 'your_secret_key'

students = {}  # This will store registered students

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        matric_no = request.form.get('matric_no')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        picture = request.files['picture']

        # Save the picture
        picture.save(os.path.join('static/uploads', picture.filename))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Store student data in a dictionary
        students[matric_no] = {
            'name': name,
            'matric_no': matric_no,
            'email': email,
            'phone': phone,
            'password': hashed_password,  # Store hashed password
            'picture': picture.filename
        }
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        matric_no = request.form.get('matric_no')
        password = request.form.get('password')

        student = students.get(matric_no)
        if student and check_password_hash(student['password'], password):  # Verify hashed password
            session['matric_no'] = matric_no
            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'matric_no' in session:
        student = students.get(session['matric_no'])

        if student is None:
            return "Student data not found. Please register again.", 404

        # Generate XML content for student data (excluding password)
        xml_data = f'''<?xml version="1.0" encoding="UTF-8"?>
        <student>
            <name>{student['name']}</name>
            <matric_no>{student['matric_no']}</matric_no>
            <email>{student['email']}</email>
            <phone>{student['phone']}</phone>
            <!-- Password is not included for security reasons -->
        </student>
        '''

        return render_template('dashboard.html', student=student, xml_data=xml_data)
    
    return redirect(url_for('login'))

@app.route('/submit_xml', methods=['POST'])
def submit_xml():
    xml_data = request.data  # Get the raw XML data from the request
    print(f"Received XML Data: {xml_data.decode('utf-8')}")  # Print or log the XML data

    # Allow XXE by using lxml with external entities
    try:
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        root = etree.fromstring(xml_data, parser)

        # Process XML data as needed (for demonstration, we print it)
        # You could extract specific data here if needed

    except etree.XMLSyntaxError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    return jsonify({"status": "success", "message": "XML received!"}), 200

@app.route('/logout')
def logout():
    session.pop('matric_no', None)
    return redirect(url_for('login'))

@app.route('/get_student_xml', methods=['POST'])
def get_student_xml():
    # Parse XML data
    xml_data = request.data.decode('utf-8')

    # Log the received XML for demonstration
    print("Received XML Request:")
    print(xml_data)

    # Extract matric number (if needed, but for demonstration, we directly use session)
    matric_no = extract_matric_no(xml_data)

    # Check session for student data
    if 'matric_no' in session and session['matric_no'] == matric_no:
        student = students.get(matric_no)

        if student is None:
            return "Student data not found.", 404

        # Generate XML content for student data (excluding password)
        xml_response = f'''
            Name: {student['name']}
            Matric No{student['matric_no']}
            Email Address: {student['email']}
            Phone Number: {student['phone']}
            
        '''

        return xml_response, 200, {'Content-Type': 'application/xml'}

    return "Unauthorized access", 401

@app.route('/check_tuition_fee', methods=['POST'])
def check_tuition_fee():
    xml_request = request.data  # Get the raw XML data from the request
    print(f"XML Tuition Request Received: {xml_request.decode('utf-8')}")  # Log the received XML

    # Allow XXE processing using lxml
    try:
        # Enable DTD loading and external entity resolution
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        root = etree.fromstring(xml_request, parser)

        # Log the matric number (XXE resolved here)
        matric_no_element = root.find('matric_no')
        matric_no = matric_no_element.text if matric_no_element is not None else "Unknown"
        print(f"Matric Number (with XXE resolution): {matric_no}")

        # Respond with tuition fee details (e.g., $3000)
        xml_response = f'''Matric No{matric_no}
            Tuition Fee = $3000
        '''

        return xml_response, 200, {'Content-Type': 'application/xml'}

    except etree.XMLSyntaxError as e:
        return jsonify({"status": "error", "message": f"XML Syntax Error: {str(e)}"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500



# This function will extract data from the XML and handle XXE
def extract_matric_no(xml_data):
    # Convert the XML data (which is a string) into bytes to handle encoding declaration
    if isinstance(xml_data, str):
        xml_data = xml_data.encode('utf-8')  # Encode the string to bytes
    
    try:
        # Set up parser with external DTD and entity resolving enabled
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        root = etree.fromstring(xml_data, parser)  # Parse the XML as bytes

        # Find the matric_no element and return its text
        matric_no_element = root.find('matric_no')

        if matric_no_element is not None:
            return matric_no_element.text
        else:
            raise ValueError("matric_no element not found in the XML data.")

    except etree.XMLSyntaxError as e:
        raise ValueError(f"XML Syntax Error: {e}")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")


if __name__ == '__main__':
    app.run(debug=True)
