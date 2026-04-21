"""
Comprehensive test suite for the High School Activity Management API.
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self, client):
        """
        Arrange: Client is ready with test activities
        Act: Make GET request to /activities endpoint
        Assert: Response status is 200 and returns all activities
        """
        # Arrange
        expected_activity_count = 3

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count

    def test_get_activities_returns_correct_structure(self, client):
        """
        Arrange: Client is ready
        Act: Get activities and inspect structure
        Assert: Each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert set(activity_data.keys()) == required_fields
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """
        Arrange: Client is ready with test data
        Act: Get activities
        Assert: Activities contain correct participant data
        """
        # Arrange
        # Reset happens via fixture with Chess Club having 2 initial participants

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert "Chess Club" in activities
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_student_succeeds(self, client):
        """
        Arrange: Prepare valid activity name and new student email
        Act: Post signup request
        Assert: Participant is added and response is 200
        """
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "alice@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_student_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_student_email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_returns_error(self, client):
        """
        Arrange: Set up existing student already signed up for activity
        Act: Try to sign up the same student again
        Assert: Returns 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_student}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Set up student email and non-existent activity
        Act: Try to sign up for activity that doesn't exist
        Assert: Returns 404 error
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        student_email = "bob@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={student_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_multiple_valid_students_in_same_activity(self, client):
        """
        Arrange: Prepare two different students
        Act: Sign up both students for same activity
        Assert: Both are added successfully
        """
        # Arrange
        activity_name = "Chess Club"
        student1 = "alice@mergington.edu"
        student2 = "bob@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={student1}"
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={student2}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        chess_participants = activities[activity_name]["participants"]
        assert student1 in chess_participants
        assert student2 in chess_participants

    def test_signup_same_student_different_activities(self, client):
        """
        Arrange: Prepare student and multiple activities
        Act: Sign student up for different activities
        Assert: Student is added to each activity
        """
        # Arrange
        student_email = "alice@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup?email={student_email}"
        )
        response2 = client.post(
            f"/activities/{activity2}/signup?email={student_email}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email in activities[activity1]["participants"]
        assert student_email in activities[activity2]["participants"]


class TestRemoveFromActivity:
    """Tests for DELETE /activities/{activity_name}/remove endpoint"""

    def test_remove_existing_participant_succeeds(self, client):
        """
        Arrange: Select activity with existing participant
        Act: Delete request to remove participant
        Assert: Participant is removed and returns 200
        """
        # Arrange
        activity_name = "Chess Club"
        participant_email = "michael@mergington.edu"  # Already enrolled

        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove?email={participant_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert participant_email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Arrange: Select activity and non-existent participant
        Act: Try to remove participant not in activity
        Assert: Returns 404 error
        """
        # Arrange
        activity_name = "Chess Club"
        nonexistent_participant = "notinactivity@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove?email={nonexistent_participant}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Set up non-existent activity name
        Act: Try to remove participant from non-existent activity
        Assert: Returns 404 error
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        participant_email = "someone@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/remove?email={participant_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_then_signup_same_participant_succeeds(self, client):
        """
        Arrange: Participant enrolled in activity
        Act: Remove participant, then sign them up again
        Assert: Both operations succeed and participant re-enrolled
        """
        # Arrange
        activity_name = "Chess Club"
        participant_email = "michael@mergington.edu"

        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/remove?email={participant_email}"
        )
        
        # Act - Sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={participant_email}"
        )

        # Assert
        assert remove_response.status_code == 200
        assert signup_response.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert participant_email in activities[activity_name]["participants"]

    def test_remove_multiple_participants_sequentially(self, client):
        """
        Arrange: Activity has multiple participants
        Act: Remove participants one by one
        Assert: Each removal succeeds and correct participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        participant1 = "michael@mergington.edu"
        participant2 = "daniel@mergington.edu"

        # Act - Remove first participant
        response1 = client.delete(
            f"/activities/{activity_name}/remove?email={participant1}"
        )

        # Act - Remove second participant
        response2 = client.delete(
            f"/activities/{activity_name}/remove?email={participant2}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert len(activities[activity_name]["participants"]) == 0


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""

    def test_complete_signup_and_removal_workflow(self, client):
        """
        Arrange: Prepare new student
        Act: Signup, verify in list, remove, verify removed
        Assert: State changes correctly at each step
        """
        # Arrange
        activity_name = "Programming Class"
        new_student = "newstudent@mergington.edu"

        # Act & Assert - Initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        assert new_student not in initial_participants

        # Act & Assert - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={new_student}"
        )
        assert signup_response.status_code == 200

        after_signup = client.get("/activities")
        after_signup_participants = after_signup.json()[activity_name]["participants"]
        assert new_student in after_signup_participants

        # Act & Assert - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/remove?email={new_student}"
        )
        assert remove_response.status_code == 200

        after_removal = client.get("/activities")
        after_removal_participants = after_removal.json()[activity_name]["participants"]
        assert new_student not in after_removal_participants

    def test_activity_state_persists_across_operations(self, client):
        """
        Arrange: Multiple students in activity
        Act: Add and remove various students
        Assert: Activity maintains correct state throughout
        """
        # Arrange
        activity = "Gym Class"
        students = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

        # Act - Add all students
        for student in students:
            client.post(f"/activities/{activity}/signup?email={student}")

        # Assert - All added
        check1 = client.get("/activities")
        participants_after_signup = check1.json()[activity]["participants"]
        for student in students:
            assert student in participants_after_signup

        # Act - Remove middle student
        client.delete(f"/activities/{activity}/remove?email={students[1]}")

        # Assert - Only middle student removed
        check2 = client.get("/activities")
        participants_after_removal = check2.json()[activity]["participants"]
        assert students[0] in participants_after_removal
        assert students[1] not in participants_after_removal
        assert students[2] in participants_after_removal
