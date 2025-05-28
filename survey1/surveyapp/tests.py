from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from surveyapp.models import Image, Participant, Response, AdviceStartTime, AdviceEndTime
from surveyapp.forms import SubmitResponse, InformedConsent, Greetings, Thanks
import json
import datetime
from surveyapp.views import get_participant
from django.test.client import RequestFactory


class ModelTests(TestCase):
    """Tests for the models in the surveyapp."""

    def setUp(self):
        """Set up test data for the models."""
        self.image = Image.objects.create(
            image_id="test_image_001",
            fake_path="img/SBIs/sbi_fake/frames/071/test_001.png",
            real_path="img/SBIs/sbi_real/frames/071/test_001.png",
            times_seen=0
        )
        self.participant = Participant.objects.create(
            ppant_id="12345",
            prolificID="test_prolific_id",
            time_started=timezone.now(),
            category="C"
        )

    def test_image_creation(self):
        """Test that an image can be created with the correct attributes."""
        self.assertEqual(self.image.image_id, "test_image_001")
        self.assertEqual(self.image.fake_path, "img/SBIs/sbi_fake/frames/071/test_001.png")
        self.assertEqual(self.image.real_path, "img/SBIs/sbi_real/frames/071/test_001.png")
        self.assertEqual(self.image.times_seen, 0)
        self.assertEqual(str(self.image), f"test_image_001 (Seen: 0 times)")

    def test_participant_creation(self):
        """Test that a participant can be created with the correct attributes."""
        self.assertEqual(self.participant.ppant_id, "12345")
        self.assertEqual(self.participant.prolificID, "test_prolific_id")
        self.assertEqual(self.participant.category, "C")
        self.assertEqual(str(self.participant), "12345")

    def test_response_creation(self):
        """Test that a response can be created with the correct attributes."""
        response = Response.objects.create(
            ppant_id=self.participant,
            time_at_submission=timezone.now(),
            time_on_question="10.5",
            response_id="test_response_001",
            image_id="test_image_001",
            choice="left",
            confidence=7,
            heatmapFill=[],
            assigned_label=1,
            gt=1,
            inconsistency_color=1,
            inconsistency_boundary=0,
            inconsistency_geometry=1,
            inconsistency_landmark=0,
            inconsistency_texture=1,
            position="left",
            is_correct=True
        )

        self.assertEqual(response.ppant_id, self.participant)
        self.assertEqual(response.response_id, "test_response_001")
        self.assertEqual(response.image_id, "test_image_001")
        self.assertEqual(response.choice, "left")
        self.assertEqual(response.confidence, 7)
        self.assertEqual(response.assigned_label, 1)
        self.assertEqual(response.gt, 1)
        self.assertEqual(response.inconsistency_color, 1)
        self.assertEqual(response.inconsistency_boundary, 0)
        self.assertEqual(response.inconsistency_geometry, 1)
        self.assertEqual(response.inconsistency_landmark, 0)
        self.assertEqual(response.inconsistency_texture, 1)
        self.assertEqual(response.position, "left")
        self.assertTrue(response.is_correct)


class FormTests(TestCase):
    def test_submit_response_form_valid(self):
        """Test that the SubmitResponse form validates correctly with valid data."""
        form_data = {
            'image': '1',
            'choice': 'left',
            'confidence': '7',
            'inconsistency_type': ['color', 'texture'],
            'heatmapFill': '[]'
        }
        form = SubmitResponse(data=form_data)
        self.assertTrue(form.is_valid())

    def test_submit_response_form_invalid(self):
        """Test that the SubmitResponse form invalidates incorrect data."""
        form_data = {
            'image': '1',
            'confidence': '7',
            'inconsistency_type': ['color', 'texture'],
            'heatmapFill': '[]'
        }
        form = SubmitResponse(data=form_data)
        self.assertFalse(form.is_valid())

        form_data = {
            'image': '1',
            'choice': 'invalid',
            'confidence': '7',
            'inconsistency_type': ['color', 'texture'],
            'heatmapFill': '[]'
        }
        form = SubmitResponse(data=form_data)
        self.assertFalse(form.is_valid())

    def test_informed_consent_form(self):
        """Test that the InformedConsent form validates correctly."""
        form_data = {
            'voluntary': True,
            'unremoveable': True,
            'anonymous': True,
            'publishable': True,
            'benefits': True,
            'nomoney': True,
            'complaint': True
        }
        form = InformedConsent(data=form_data)
        self.assertTrue(form.is_valid())


class ViewTests(TestCase):
    """Tests for the views in the surveyapp."""

    def setUp(self):
        self.client = Client()
        self.image = Image.objects.create(
            image_id="test_image_001",
            fake_path="img/SBIs/sbi_fake/frames/071/test_001.png",
            real_path="img/SBIs/sbi_real/frames/071/test_001.png",
            times_seen=0
        )

        self.participant = Participant.objects.create(
            ppant_id="12345",
            prolificID="test_prolific_id",
            time_started=timezone.now(),
            category="C"
        )

    def test_intro_page(self):
        """Test that the intro page loads correctly."""
        response = self.client.get(reverse('intro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'entrancePage.html')

    def test_help_page(self):
        """Test that the help page loads correctly."""
        session = self.client.session
        session['ppant_id'] = "12345"
        session.save()

        response = self.client.get(reverse('introHelp'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'introhelp.html')

    def test_example_task_page(self):
        """Test that the example task page loads correctly."""
        session = self.client.session
        session['ppant_id'] = "12345"
        session.save()

        response = self.client.get(reverse('exampleTask'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exampleTask.html')

    def test_main_page_redirect_without_participant(self):
        """Test that the main page redirects to intro if no participant is in session."""
        response = self.client.get(reverse('main1'))
        self.assertRedirects(response, reverse('intro'))

    def test_main_page_with_participant(self):
        """Test that the main page loads correctly with a participant in session."""

        session = self.client.session
        session['ppant_id'] = "12345"
        session.save()

        response = self.client.get(reverse('main1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'page1.html')


class FunctionTests(TestCase):
    """Tests for specific functions in the views."""

    def setUp(self):
        self.image1 = Image.objects.create(
            image_id="test_image_001",
            fake_path="img/SBIs/sbi_fake/frames/071/test_001.png",
            real_path="img/SBIs/sbi_real/frames/071/test_001.png",
            times_seen=0
        )

        self.image2 = Image.objects.create(
            image_id="test_image_002",
            fake_path="img/SBIs/sbi_fake/frames/071/test_002.png",
            real_path="img/SBIs/sbi_real/frames/071/test_002.png",
            times_seen=1
        )

        self.participant = Participant.objects.create(
            ppant_id="12345",
            prolificID="test_prolific_id",
            time_started=timezone.now(),
            category="C"
        )

        self.response = Response.objects.create(
            ppant_id=self.participant,
            time_at_submission=timezone.now(),
            time_on_question="10.5",
            response_id="test_response_001",
            image_id="test_image_001",
            choice="left",
            confidence=7,
            heatmapFill=[],
            assigned_label=1,
            gt=1,
            inconsistency_color=1,
            inconsistency_boundary=0,
            inconsistency_geometry=1,
            inconsistency_landmark=0,
            inconsistency_texture=1,
            position="left",
            is_correct=True
        )

    def test_get_participant(self):
        """Test the get_participant function."""

        factory = RequestFactory()
        request = factory.get('/')
        request.session = {'ppant_id': "12345"}

        # Test getting an existing participant
        participant = get_participant(request)
        self.assertEqual(participant, self.participant)

        # Test with non-existent participant ID
        request.session = {'ppant_id': "99999"}
        participant = get_participant(request)
        self.assertIsNone(participant)

        # Test with no participant ID in session
        request.session = {}
        participant = get_participant(request)
        self.assertIsNone(participant)

    def test_get_participant_responses(self):
        """Test the get_participant_responses function."""
        from surveyapp.views import get_participant_responses

        # Test with a participant that has responses
        img_nums, correct_count = get_participant_responses(self.participant)
        self.assertEqual(img_nums, 1) 
        self.assertEqual(correct_count, 1)  

        # Create another response with the same response_id but incorrect
        Response.objects.create(
            ppant_id=self.participant,
            time_at_submission=timezone.now(),
            time_on_question="5.2",
            response_id="test_response_001",  # Same response_id
            image_id="test_image_002",
            choice="right",
            confidence=5,
            heatmapFill=[],
            assigned_label=0,
            gt=0,
            inconsistency_color=0,
            inconsistency_boundary=0,
            inconsistency_geometry=0,
            inconsistency_landmark=0,
            inconsistency_texture=0,
            position="right",
            is_correct=False
        )

        img_nums, correct_count = get_participant_responses(self.participant)
        self.assertEqual(img_nums, 1)  
        self.assertEqual(correct_count, 1)  

        Response.objects.create(
            ppant_id=self.participant,
            time_at_submission=timezone.now(),
            time_on_question="7.3",
            response_id="test_response_002",  
            image_id="test_image_002",
            choice="right",
            confidence=8,
            heatmapFill=[],
            assigned_label=1,
            gt=1,
            inconsistency_color=0,
            inconsistency_boundary=1,
            inconsistency_geometry=0,
            inconsistency_landmark=1,
            inconsistency_texture=0,
            position="right",
            is_correct=True
        )


        img_nums, correct_count = get_participant_responses(self.participant)
        self.assertEqual(img_nums, 2) 
        self.assertEqual(correct_count, 2) 


class IntegrationTests(TestCase):
    """Integration tests for the survey flow."""

    def setUp(self):
        self.image = Image.objects.create(
            image_id="test_image_001",
            fake_path="img/SBIs/sbi_fake/frames/071/test_001.png",
            real_path="img/SBIs/sbi_real/frames/071/test_001.png",
            times_seen=0
        )

        self.client = Client()

    def test_survey_flow(self):
        """Test the complete survey flow from intro to main page."""
        response = self.client.get(reverse('intro'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('intro'))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Participant.objects.count(), 1)

        response = self.client.get(reverse('introHelp'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('introHelp'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('exampleTask'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('exampleTask'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('main1'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Question')
        self.assertContains(response, '/ 20')

        participant_id = self.client.session.get('ppant_id')
        self.assertIsNotNone(participant_id)

        participant = Participant.objects.get(ppant_id=participant_id)
        self.assertEqual(participant.category, 'C')
