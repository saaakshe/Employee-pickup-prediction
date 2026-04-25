from sqlalchemy import create_engine
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
from flask import Flask, request, jsonify
from math import radians, cos, sin, asin, sqrt
from flask_cors import CORS

# MySQL connection setup
db_url = 'mysql+mysqlconnector://jayesh:12345678@mysql:3306/employeePrediction'
engine = create_engine(db_url)

# Load the dataset from MySQL
query = "SELECT shift_date, employeeid, latitude, longitude, employee_latitude, employee_longitude FROM employeedata"
df = pd.read_sql(query, engine)

# Ensure dataset has the expected columns
expected_columns = ['shift_date', 'employeeid', 'latitude', 'longitude', 'employee_latitude', 'employee_longitude']
if not all(col in df.columns for col in expected_columns):
    raise ValueError("Dataset does not contain the expected columns.")

# Remove any rows with NaN values
df.dropna(subset=expected_columns, inplace=True)

# Haversine formula to calculate distance between two points in meters
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return 1000 * c * r

# Function to predict pickup location for an employee
def predict_location(employee_id):
    group = df[df['employeeid'] == employee_id]
    pickup_points = group[['latitude', 'longitude']].values

    if len(pickup_points) < 2:
        return None  # Not enough points for PCA or clustering

    # Apply PCA
    pca = PCA(n_components=2)
    pickup_points_pca = pca.fit_transform(pickup_points)
    
    # Determine number of clusters
    n_clusters = min(3, len(pickup_points_pca))
    
    if n_clusters > 1:
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        kmeans.fit(pickup_points_pca)
        cluster_centers_pca = kmeans.cluster_centers_
        cluster_centers = pca.inverse_transform(cluster_centers_pca)
        
        # Registered location
        registered_location = group[['employee_latitude', 'employee_longitude']].iloc[0].values
        
        # Compute Haversine distances to the registered location
        distances = np.array([haversine(lon, lat, registered_location[1], registered_location[0])
                              for lat, lon in cluster_centers])
        
        # Find the closest cluster center
        closest_cluster_center = cluster_centers[np.argmin(distances)]
    else:
        closest_cluster_center = pickup_points[0]

    return closest_cluster_center

def get_unique_employee_ids():
    return df['employeeid'].unique().tolist()


# Flask API
app = Flask(__name__)
CORS(app)


@app.route('/employee_ids', methods=['GET'])
def get_employee_ids():
    employee_ids = get_unique_employee_ids()
    return jsonify({"employee_ids": employee_ids})


@app.route('/employee_locations', methods=['GET'])
def get_employee_locations():
    employee_id = request.args.get('employeeid', type=int)

    if employee_id is None:
        return jsonify({"error": "employeeid is required"}), 400

    group = df[df['employeeid'] == employee_id]

    if group.empty:
        return jsonify({"error": "employeeid not found"}), 404

    locations = group[['latitude', 'longitude']].values.tolist()

    return jsonify({
        "employeeid": employee_id,
        "locations": locations
    })


@app.route('/all_predictions', methods=['GET'])
def get_all_predictions():
    predictions = []
    employee_ids = df['employeeid'].unique()

    for employee_id in employee_ids:
        predicted_location = predict_location(employee_id)
        
        if predicted_location is not None:
            predictions.append({
                "employeeid": employee_id,
                "predicted_latitude": predicted_location[0],
                "predicted_longitude": predicted_location[1]
            })
    
    return jsonify(predictions)


@app.route('/employee_data', methods=['GET'])
def get_employee_data():
    employees_data = df.to_dict(orient='records')
    return jsonify(employees_data)


@app.route('/predict_location', methods=['GET'])
def get_prediction():
    employee_id = request.args.get('employeeid', type=int)
    
    if employee_id is None:
        return jsonify({"error": "employeeid is required"}), 400
    
    predicted_location = predict_location(employee_id)
    
    if predicted_location is None:
        return jsonify({"error": "Not enough data to predict location"}), 404
    
    return jsonify({
        "employeeid": employee_id,
        "predicted_latitude": predicted_location[0],
        "predicted_longitude": predicted_location[1]
    })

@app.route('/registered_location', methods=['GET'])
def get_registered_location():
    employee_id = request.args.get('employeeid', type=int)
    
    if employee_id is None:
        return jsonify({"error": "employeeid is required"}), 400
    
    group = df[df['employeeid'] == employee_id]
    if group.empty:
        return jsonify({"error": "employeeid not found"}), 404
    
    registered_location = group[['employee_latitude', 'employee_longitude']].iloc[0].values
    
    return jsonify({
        "employeeid": employee_id,
        "registered_latitude": registered_location[0],
        "registered_longitude": registered_location[1]
    })

@app.route('/pickup_points', methods=['GET'])
def get_pickup_points():
    employee_id = request.args.get('employeeid', type=int)
    
    if employee_id is None:
        return jsonify({"error": "employeeid is required"}), 400
    
    group = df[df['employeeid'] == employee_id]
    if group.empty:
        return jsonify({"error": "employeeid not found"}), 404
    
    pickup_points = group[['latitude', 'longitude']].values.tolist()
    
    return jsonify({
        "employeeid": employee_id,
        "pickup_points": pickup_points
    })

@app.route('/employee_within_distance', methods=['GET'])
def get_employees_within_distance():
    # Get distance from query parameters
    distance_limit = request.args.get('distance', type=float)

    if distance_limit is None:
        return jsonify({"error": "distance is required"}), 400

    # Initialize list for employee IDs that match the criteria
    matching_employee_ids = []

    # Loop through all unique employee IDs
    for employee_id in get_unique_employee_ids():
        predicted_location = predict_location(employee_id)

        if predicted_location is not None:
            # Get the registered location for this employee
            group = df[df['employeeid'] == employee_id]
            registered_location = group[['employee_latitude', 'employee_longitude']].iloc[0].values

            # Calculate the distance between predicted and registered locations
            distance = haversine(predicted_location[1], predicted_location[0], 
                                 registered_location[1], registered_location[0])

            # If the distance is less than the query param, add the employee ID to the list
            if distance < distance_limit:
                matching_employee_ids.append(employee_id)

    # Return the list of employee IDs that match the distance criteria
    return jsonify({"employee_ids": matching_employee_ids})




if __name__ == '__main__':
    app.run(debug=True,resources={r"/*": {"origins": "*"}},host="0.0.0.0", port=5001)
