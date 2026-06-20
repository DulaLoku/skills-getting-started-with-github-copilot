import src.app as app_module


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_expected_structure(client):
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert required_fields.issubset(payload["Chess Club"].keys())
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_success_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    route = "/activities/Chess%20Club/signup"
    assert email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(route, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    route = "/activities/Unknown%20Activity/signup"

    # Act
    response = client.post(route, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]
    route = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(route, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_success_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = app_module.activities[activity_name]["participants"][0]
    route = "/activities/Chess%20Club/participants"
    assert email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(route, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    route = "/activities/Unknown%20Activity/participants"

    # Act
    response = client.delete(route, params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    route = "/activities/Chess%20Club/participants"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(route, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
