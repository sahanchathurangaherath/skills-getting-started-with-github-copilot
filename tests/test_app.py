"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and regional tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in school productions and develop theatrical skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, sculpture, and digital art techniques",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking through competitive debate",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "isabella@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for science competitions",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ryan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_state)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(initial_state)


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_redirect_to_static(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
        assert data["Chess Club"]["max_participants"] == 12
        assert len(data["Chess Club"]["participants"]) == 2

    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignUp:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_registered(self, client, reset_activities):
        """Test signup for an activity the student is already registered for"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple different students signing up"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Tennis%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Tennis Club"]["participants"]
        for email in emails:
            assert email in participants


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistration for a student not signed up"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_then_signup(self, client, reset_activities):
        """Test that a student can re-signup after unregistering"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Try to sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student is registered again
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_unregister_multiple(self, client, reset_activities):
        """Test signing up and unregistering multiple students"""
        activity = "Art Studio"
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]
        
        # Sign up all students
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Unregister first student
        response = client.post(f"/activities/{activity}/unregister?email={emails[0]}")
        assert response.status_code == 200
        
        # Verify participants
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        assert emails[0] not in participants
        assert emails[1] in participants
        assert emails[2] in participants

    def test_activity_availability_after_operations(self, client, reset_activities):
        """Test that availability is correctly calculated after signup/unregister"""
        activity = "Chess Club"
        max_participants = 12
        initial_count = len(activities[activity]["participants"])
        
        # Get initial availability
        response = client.get("/activities")
        available_before = max_participants - initial_count
        
        # Sign up a new student
        client.post(f"/activities/{activity}/signup?email=newstudent@mergington.edu")
        
        # Get updated activities (in a real scenario, we'd check the client response)
        response = client.get("/activities")
        current_count = len(response.json()[activity]["participants"])
        available_after = max_participants - current_count
        
        assert available_after == available_before - 1
