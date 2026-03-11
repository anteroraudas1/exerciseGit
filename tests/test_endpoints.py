"""
Comprehensive test suite for Mergington High School Activities API endpoints.

This module contains tests for all API endpoints organized by functionality,
using the AAA (Arrange-Act-Assert) testing pattern for clarity and maintainability.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Arrange: API with 9 activities in database
        Act: Send GET request to /activities
        Assert: Response status 200, contains all 9 activities
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
    
    def test_get_activities_contains_expected_activity_names(self, client, fresh_activities):
        """
        Arrange: Database with named activities
        Act: Get all activities
        Assert: Response includes all expected activity names
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        expected_names = {
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Swimming Club", "Art Studio",
            "Drama Club", "Debate Team", "Science Club"
        }
        assert set(activities.keys()) == expected_names
    
    def test_get_activities_has_correct_structure(self, client, fresh_activities):
        """
        Arrange: Activities endpoint
        Act: Get all activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity in activities.values():
            assert required_fields.issubset(set(activity.keys()))
            assert isinstance(activity["description"], str)
            assert isinstance(activity["schedule"], str)
            assert isinstance(activity["max_participants"], int)
            assert isinstance(activity["participants"], list)
    
    def test_get_activities_participants_are_emails(self, client, fresh_activities):
        """
        Arrange: Activities with participants
        Act: Get all activities
        Assert: All participants are valid email strings
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity in activities.values():
            for participant in activity["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_succeeds(self, client, fresh_activities):
        """
        Arrange: Fresh database, new student email, valid activity
        Act: POST signup request for Basketball Team with new email
        Assert: Status 200, message confirms signup, participants list updated
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1
        assert "Signed up" in response.json()["message"]
    
    def test_signup_duplicate_student_fails(self, client, fresh_activities):
        """
        Arrange: Fresh database, student already signed up for Chess Club
        Act: Try to signup same student again
        Assert: Status 400, error message indicates duplicate signup
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, fresh_activities):
        """
        Arrange: Fresh database, invalid activity name
        Act: POST signup for non-existent activity
        Assert: Status 404, error message indicates activity not found
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_response_format(self, client, fresh_activities):
        """
        Arrange: Valid signup request
        Act: POST signup request
        Assert: Response JSON contains message field with expected text format
        """
        # Arrange
        activity_name = "Swimming Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]


class TestUnregister:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_unregister_existing_participant_succeeds(self, client, fresh_activities):
        """
        Arrange: Fresh database, participant exists in Chess Club
        Act: DELETE participant from activity
        Assert: Status 200, participant removed from list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_nonexistent_participant_fails(self, client, fresh_activities):
        """
        Arrange: Fresh database, participant not in Gym Class
        Act: DELETE non-existent participant
        Assert: Status 404, error indicating participant not found
        """
        # Arrange
        activity_name = "Gym Class"
        email = "notamember@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, fresh_activities):
        """
        Arrange: Fresh database, invalid activity name
        Act: DELETE participant from non-existent activity
        Assert: Status 404, error indicating activity not found
        """
        # Arrange
        activity_name = "Fake Club"
        email = "someone@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
    
    def test_unregister_response_format(self, client, fresh_activities):
        """
        Arrange: Valid unregister request for existing participant
        Act: DELETE participant
        Assert: Response JSON contains message field
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        data = response.json()
        assert "message" in data


class TestEdgeCases:
    """Integration tests for cross-endpoint scenarios and edge cases."""
    
    def test_signup_then_get_reflects_change(self, client, fresh_activities):
        """
        Arrange: Fresh database
        Act: Signup new student, then GET activities
        Assert: Participant appears in activity's participant list
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "newplayer@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_unregister_then_get_reflects_change(self, client, fresh_activities):
        """
        Arrange: Fresh database with participant in activity
        Act: Unregister participant, then GET activities
        Assert: Participant no longer in activity's participant list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]
    
    def test_signup_unregister_signup_workflow(self, client, fresh_activities):
        """
        Arrange: Fresh database
        Act: Signup → unregister → signup same student
        Assert: All operations succeed, participant finally in list
        """
        # Arrange
        activity_name = "Swimming Club"
        email = "swimmer@mergington.edu"
        
        # Act & Assert - First signup succeeds
        response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response1.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
        
        # Act & Assert - Unregister succeeds
        response2 = client.delete(f"/activities/{activity_name}/participants/{email}")
        assert response2.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
        
        # Act & Assert - Re-signup succeeds
        response3 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response3.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
    
    def test_multiple_participants_can_signup(self, client, fresh_activities):
        """
        Arrange: Fresh database, empty activity
        Act: Multiple students sign up for same activity
        Assert: All participants successfully added
        """
        # Arrange
        activity_name = "Art Studio"
        emails = ["artist1@mergington.edu", "artist2@mergington.edu", "artist3@mergington.edu"]
        
        # Act
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Assert
        response = client.get("/activities")
        activities = response.json()
        for email in emails:
            assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(emails)
    
    def test_unregister_one_participant_keeps_others(self, client, fresh_activities):
        """
        Arrange: Fresh database with multiple participants
        Act: Unregister one participant from Gym Class
        Assert: Other participants remain in the activity
        """
        # Arrange
        activity_name = "Gym Class"
        other_email = "olivia@mergington.edu"  # Should remain
        
        # Act
        client.delete(f"/activities/{activity_name}/participants/john@mergington.edu")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert other_email in activities[activity_name]["participants"]
        assert "john@mergington.edu" not in activities[activity_name]["participants"]
