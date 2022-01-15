# Tree App Capstone Project

## Tree App
This project is a tree-planting app, it can: 

1. Add new forests
2. Add new farmers
3. Plant new trees

The app url is https://tree-app-udacity.herokuapp.com/

## Getting Started

### Pre-requisites and Local Development 
Developers using this project should already have Python3, pip and node installed on their local machines.

#### Backend

From the backend folder run `pip install -r requirements.txt`. All required packages are included in the requirements file. 

To run the application run the following commands from the backend folder: 
```
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

The application is run on `http://127.0.0.1:5000/` by default.

#### Frontend

The app does not have a frontend.


### Tests
In order to run tests, run the following commands from the backend folder: 

```
dropdb tree_test
createdb tree_test
psql tree_test < tree.psql
python test_app.py
```

The first time you run the tests, omit the dropdb command. 

All tests are kept in that file and should be maintained as updates are made to app functionality. 

## API Reference

### Getting Started
- Base URL: https://tree-app-udacity.herokuapp.com/
- Authentication: This version of the application does not require authentication or API keys.

### Authorization
Certain actions require authorization to be performed. Authorization is granted according to the role of user. 

#### Roles
- Admin: Can perform all actions
- Farmer: Can plant trees

#### Login info
Login endpoint: https://tree-app-udacity.herokuapp.com/login
Login to get access token: https://tree-app.eu.auth0.com/authorize?audience=tree&response_type=token&client_id=oKWhbpnbNRWsmcY52NgNmbTSTnEyr7vA&redirect_uri=https://tree-app-udacity.herokuapp.com/

Use the following credentials to login as different roles

- Admin
    - email: admin@test.com
    - password: Admintest1$

- Farmer
    - email: farmer@test.com
    - password: Farmer95$

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return four error types when requests fail:
- 404: Resource Not Found
- 422: Not Processable 
- 500: Internal Server Error
- 401: Unauthorized Action

### Endpoints 
#### GET /trees
- General:
    - Returns a list of tree objects, success value, and total number of trees
- Sample: `curl https://tree-app-udacity.herokuapp.com/trees`

```
{
    "number_of_trees": 5,
    "success": true,
    "trees": [
        {
            "farmer_id": 1,
            "forest_id": 1,
            "id": 1,
            "name": "Palm"
        },
        {
            "farmer_id": 1,
            "forest_id": 1,
            "id": 2,
            "name": "Palm"
        },
        {
            "farmer_id": 1,
            "forest_id": 1,
            "id": 3,
            "name": "Palm"
        },
        {
            "farmer_id": 1,
            "forest_id": 1,
            "id": 4,
            "name": "Palm"
        },
        {
            "farmer_id": 1,
            "forest_id": 1,
            "id": 5,
            "name": "Palm"
        }
    ]
}
```

#### GET /forests
- General:
    - Returns a list of forest objects, success value and total number of forests

- Sample: `curl https://tree-app-udacity.herokuapp.com/forests`
```
{
    "forests": [
        {
            "id": 1,
            "location": "Italy",
            "name": "First Forest"
        }
    ],
    "number_of_forests": 1,
    "success": true
}
```

#### GET /farmers
- General:
    - Returns a list of farmer objects, success value and total number of farmers
- Authorization: requires no authorization
- Sample: `curl https://tree-app-udacity.herokuapp.com/farmers`
```
{
    "farmers": [
        {
            "id": 1,
            "name": "First Farmer"
        }
    ],
    "number_of_farmers": 1,
    "success": true
}
```

#### GET /farmers/{farmer_id}
- General:
    - Returns the farmer object corresponding to the queried id, success value, total number of farmers planted by that farmers and a count of trees planted by that farmer, grouped by type.
- Authorization: requires no authorization
- Sample: `curl https://tree-app-udacity.herokuapp.com/farmers/1`
```
{
    "farmer": {
        "id": 1,
        "name": "First Farmer"
    },
    "number_of_trees": 5,
    "success": true,
    "trees": {
        "Palm": 5
    }
}
```

#### GET /forests/{forest_id}
- General:
    - Returns the forest object corresponding to the queried id, success value, total number of farmers planted in that forest, a count of trees planted in that forest grouped by type and a count of farmers that planted in that forest.
- Authorization: requires no authorization
- Sample: `curl https://tree-app-udacity.herokuapp.com/forests/1`
```
{
    "farmer_count": 1,
    "forest": {
        "id": 1,
        "location": "Italy",
        "name": "First Forest"
    },
    "number_of_trees": 5,
    "success": true,
    "trees": {
        "Palm": 5
    }
}
```

#### POST /farmers
- General:
    - Creates a new farmer using the submitted name. Returns the newly created farmer object, success value and total farmers.
- Authorization: 
    - Requires `post:farmer` authorization
    - Only `Admin` role can perform this action
- Sample create new farmer: `curl -X POST -H "Content-Type: application/json" -d '{"name": "Cristiano Ronaldo"}' https://tree-app-udacity.herokuapp.com/farmers`
```
{
    "created": {
        "id": 2,
        "name": "Cristiano Ronaldo"
    },
    "success": true,
    "total_farmers": 2
}
```

#### PATCH /farmers/{farmer_id}
- General:
    - Updates the selected farmer using the submitted name. Returns the updated farmer object and success value.
- Authorization: 
    - Requires `patch:farmer` authorization
    - Only `Admin` role can perform this action
- Sample update farmer: `curl -X PATCH -H "Content-Type: application/json" -d '{"name": "Danny De Vito"}' https://tree-app-udacity.herokuapp.com/farmers/2`
```
{
    "modified": {
        "id": 2,
        "name": "Danny De Vito"
    },
    "success": true
}
```

#### POST /forests
- General:
    - Creates a new forest using the submitted name and location. Returns the newly created forest object, success value and total forests.
- Authorization: 
    - Requires `post:forest` authorization
    - Only `Admin` role can perform this action
- Sample create new forest: `curl -X POST -H "Content-Type: application/json" -d '{"name": "Tropical Forest", "location":"Siberia"}' https://tree-app-udacity.herokuapp.com/forests`
```
{
    "created": {
        "id": 2,
        "location": "Siberia",
        "name": "Tropical Forest"
    },
    "forests": [
        {
            "id": 1,
            "location": "Italy",
            "name": "First Forest"
        },
        {
            "id": 2,
            "location": "Siberia",
            "name": "Tropical Forest"
        }
    ],
    "success": true
}
```

#### POST /trees
- General:
    - Creates a number of new tree objects using the submitted name, forest id, farmer id and quantity. Returns a list of the newly created tree objects, success value and total trees.
    - Trees must belong to a farmer and a forest
- Authorization: 
    - Requires `post:tree` authorization
    - Both `Admin` and `Farmer` roles can perform this action
- Sample create new trees `curl -X POST -H "Content-Type: application/json" -d '{"name": "Cactus", "farmer_id":2, "forest_id":2, "quantity":2}' https://tree-app-udacity.herokuapp.com/trees`
```
{
    "created": [
        {
            "farmer_id": 2,
            "forest_id": 2,
            "id": 6,
            "name": "Cactus"
        },
        {
            "farmer_id": 2,
            "forest_id": 2,
            "id": 7,
            "name": "Cactus"
        }
    ],
    "success": true,
    "total_trees": 7
}
```

#### DELETE /trees/{tree_id}
- General:
    - Deletes the tree of the given ID if it exists. Returns the id of the deleted tree, success value and total trees.
- `curl -X DELETE https://tree-app-udacity.herokuapp.com/trees/7`
```
{
    "deleted": 7,
    "success": true,
    "total_trees": 6
}
```
