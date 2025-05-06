import datetime
import json
import random

from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from surveyapp.forms import SubmitResponse, InformedConsent, Greetings, Thanks
from surveyapp.models import Image, Participant, Response, AdviceStartTime, AdviceEndTime
from django.template import RequestContext
from collections import Counter

def handler500(request, *args, **argv):
    response = render(None,'500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


def index(request):
    return HttpResponse("Hello, you've somehow reached the index page. Please go to .../intro instead of .../index")


def introPage(request):
    print('start page')

    cons_so_far = AdviceStartTime.objects.all()
    ppants_consented = []
    for c in cons_so_far:
        ppants_consented += [c.ppant_id]

    request.session['numsYet'] = []
    request.session.save()  # Ensure session is saved
    ppants = Participant.objects.all()

    # All users get the same experience, no category assignment needed
    request.session['category'] = 'C'  # Using category C as the default for all users
    request.session.save()  # Ensure session is saved

    #assigninig a random ppant id!
    ppant_rand = random.randint(0, 999999)+1
    while ppant_rand in [p.ppant_id for p in ppants]:
        ppant_rand = random.randint(0, 999999) + 1

    request.session['ppant_id'] = ppant_rand
    request.session.save()  # Ensure session is saved
    print("ppant is:",ppant_rand)

    context = {}

    if request.method == 'POST':
        print("posting")
        ppant_id = request.session.get('ppant_id', 'default')
        print("ppant is:",ppant_id)
        time_now = datetime.datetime.now()
        category = request.session.get('category', 'default')

        # Create participant without prolific ID
        ppant_instance = Participant(
            ppant_id = ppant_id,
            prolificID = "",  # Empty string instead of prolific ID
            time_started = time_now,
            category = category)
        ppant_instance.save()
        return redirect(helpPage)

    return render(request, 'entrancePage.html', context=context)



def exampleTask(request):
    if request.method == 'POST':
        # submit to database timelog of: advicetype, participantid, time
        time_now = datetime.datetime.now()
        this_ppant_id = request.session.get('ppant_id', 'default')
        ppant_query = Participant.objects.filter(ppant_id=this_ppant_id)

        # Initialize ppant_instance to None
        ppant_instance = None

        # Try to get the participant instance
        for i in ppant_query:
            ppant_instance = i
            break

        # If no participant found, redirect to intro page
        if ppant_instance is None:
            print("Participant not found, redirecting to intro page")
            return redirect('intro')
        advice_time_instance = AdviceEndTime(
            ppant_id=ppant_instance,
            advice_type='control',
            time_at_submission=time_now
        )
        advice_time_instance.save()
        return redirect(mainQuPage)

    context = {
        'category': request.session.get('category', 'default'),
    }
    return render(request, 'exampleTask.html', context=context)



def familiarizationPage(request):
    randomTwenty = ['1', '2', '3', '4', '5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']
    random.shuffle(randomTwenty)

    if request.method == 'POST':
        # submit to database timelog of: advicetype, participantid, time
        time_now = datetime.datetime.now()
        this_ppant_id = request.session.get('ppant_id', 'default')
        ppant_query = Participant.objects.filter(ppant_id=this_ppant_id)

        # Initialize ppant_instance to None
        ppant_instance = None

        # Try to get the participant instance
        for i in ppant_query:
            ppant_instance = i
            break

        # If no participant found, redirect to intro page
        if ppant_instance is None:
            print("Participant not found, redirecting to intro page")
            return redirect('intro')
        advice_time_instance = AdviceEndTime(
            ppant_id=ppant_instance,
            advice_type='control',
            time_at_submission=time_now
        )
        advice_time_instance.save()
        return redirect(mainQuPage)

    context = {
        'randomTwenty': randomTwenty,
    }
    return render(request, 'introfamiliarization.html', context=context)


def helpPage(request):
    maj = ['a', 'b', 'c', 'd']
    random.shuffle(maj)
    minA = ['1', '2', '3']
    random.shuffle(minA)
    minB = ['1', '2', '3', '4']
    random.shuffle(minB)
    minC = ['1', '2', '3']
    random.shuffle(minC)
    minD = ['1']
    random.shuffle(minD)

    if request.method == 'POST':
        # submit to database timelog of: advicetype, participantid, time
        time_now = datetime.datetime.now()
        print("Help",time_now)
        this_ppant_id = request.session.get('ppant_id', 'default')
        ppant_query = Participant.objects.filter(ppant_id=this_ppant_id)

        # Initialize ppant_instance to None
        ppant_instance = None

        # Try to get the participant instance
        for i in ppant_query:
            ppant_instance = i
            break

        # If no participant found, redirect to intro page
        if ppant_instance is None:
            print("Participant not found, redirecting to intro page")
            return redirect('intro')
        advice_time_instance = AdviceEndTime(
            ppant_id=ppant_instance,
            advice_type='control',
            time_at_submission=time_now
        )
        advice_time_instance.save()
        return redirect(exampleTask)

    context = {
        'maj': maj,
        'minA': minA,
        'minB': minB,
        'minC': minC,
        'minD': minD,
    }
    return render(request, 'introhelp.html', context=context)


def select_image(request, all_images):
    """Select an image for the current question based on participant history."""
    ppant_instance = get_participant(request)
    if ppant_instance is None:
        return random.choice(all_images)

    # Get responses for this participant
    responses = Response.objects.filter(ppant_id=ppant_instance)

    # Get unique image IDs that have been seen
    # First, get the image_id strings from responses
    seen_image_id_strings = list(responses.values_list('image_id', flat=True).distinct())

    # Then, get the actual Image objects with these image_id strings
    # This is needed because the Response.image_id field stores the image_id string, not the Image.id
    seen_images = []
    if seen_image_id_strings:
        # Create a list to store image IDs
        seen_image_ids = []

        # For each image in the database
        for image in Image.objects.all():
            # Check if its image_id is in the list of seen image_id strings
            if image.image_id in seen_image_id_strings:
                seen_image_ids.append(image.id)

        # Exclude already seen images
        unseen_images = all_images.exclude(id__in=seen_image_ids)
    else:
        # If no images have been seen, all images are unseen
        unseen_images = all_images

    # If all images have been seen, allow any image
    if not unseen_images:
        return random.choice(all_images)

    return random.choice(unseen_images)

def prepare_context(request, selected_image, left_image_path, right_image_path,
                    img_nums_so_far_this_ppant, correct_answers_count, how_many_qus, form):
    """Prepare the context for rendering the main question page."""
    context = {
        'selected_image': selected_image,
        'left_image_path': left_image_path,
        'right_image_path': right_image_path,
        'img_nums_so_far_this_ppant': img_nums_so_far_this_ppant,
        'correct_answers_count': correct_answers_count,
        'how_many_qus': how_many_qus,
        'total_questions': how_many_qus,
        'form': form,
        'question_number': img_nums_so_far_this_ppant + 1,
        'current_question_number': img_nums_so_far_this_ppant + 1,
        'questions_attempted': img_nums_so_far_this_ppant,
        'num': selected_image.id,
        'progress_percentage': (img_nums_so_far_this_ppant / how_many_qus) * 100,
    }
    return context


def determine_image_placement(request, selected_image):
    """Determine the placement of the images (left/right) and the correct answer."""
    # Randomly determine if fake image should be on left or right
    if 'fake_on_left' not in request.session:
        fake_on_left = random.choice([True, False])
        request.session['fake_on_left'] = fake_on_left
    else:
        fake_on_left = request.session.get('fake_on_left')

    # Store the current image ID in session
    request.session['current_image_id'] = selected_image.id
    request.session.save()

    # Determine paths and set correct answer
    if fake_on_left:
        left_image_path = selected_image.fake_path
        right_image_path = selected_image.real_path
        correct_answer = 'left'
    else:
        left_image_path = selected_image.real_path
        right_image_path = selected_image.fake_path
        correct_answer = 'right'

    # Store the correct answer in session for feedback
    request.session['correct_answer'] = correct_answer
    request.session.save()

    return left_image_path, right_image_path, correct_answer

def clear_session_data(request):
    """Clear session data after a question is answered."""
    if 'current_image_id' in request.session:
        del request.session['current_image_id']
    if 'fake_on_left' in request.session:
        del request.session['fake_on_left']
    request.session.save()

def survey_complete(request):
    """View for the survey completion page."""
    ppant_instance = get_participant(request)
    if ppant_instance is None:
        return redirect('intro')

    img_nums_so_far_this_ppant, correct_answers_count = get_participant_responses(ppant_instance)

    # Total number of questions in the survey
    total_questions = 20

    # Calculate accuracy percentage
    accuracy_percentage = 0
    if img_nums_so_far_this_ppant > 0:
        accuracy_percentage = (correct_answers_count / img_nums_so_far_this_ppant) * 100

    # Determine achievement title based on accuracy
    achievement = "Rookie Detective"
    if accuracy_percentage >= 90:
        achievement = "Master Detective"
    elif accuracy_percentage >= 75:
        achievement = "Senior Detective"
    elif accuracy_percentage >= 60:
        achievement = "Detective"
    elif accuracy_percentage >= 40:
        achievement = "Junior Detective"

    context = {
        'correct_answers_count': correct_answers_count,
        'questions_attempted': img_nums_so_far_this_ppant,
        'total_questions': total_questions,
        'accuracy_percentage': accuracy_percentage,
        'achievement': achievement
    }

    return render(request, 'endsurvey.html', context)

def check_survey_completion(request, img_nums_so_far_this_ppant, correct_answers_count, how_many_qus):
    """Check if the participant has completed the survey."""
    if img_nums_so_far_this_ppant >= how_many_qus:
        # Optionally handle survey completion (e.g., show results, thank you page)
        return redirect('survey_complete')  # Adjust 'survey_complete' to your final page URL
    return None

def get_participant_responses(ppant_instance):
    """Retrieve the number of questions answered and the number of correct answers."""
    responses = Response.objects.filter(ppant_id=ppant_instance)
    # Count unique response_ids to avoid counting each question twice
    unique_response_ids = responses.values_list('response_id', flat=True).distinct()
    img_nums_so_far = len(unique_response_ids)

    # Count correct answers by unique response_ids
    correct_response_ids = responses.filter(is_correct=True).values_list('response_id', flat=True).distinct()
    correct_answers_count = len(correct_response_ids)

    return img_nums_so_far, correct_answers_count

def get_participant(request):
    """Retrieve the participant instance from the session or request."""
    ppant_id = request.session.get('ppant_id')
    if ppant_id:
        try:
            # Get the participant by ppant_id field, not the auto-generated primary key
            participants = Participant.objects.filter(ppant_id=ppant_id)
            if participants.exists():
                return participants.first()
        except Exception:
            return None
    return None

def calculate_time_on_question(request, time_now):
    """Calculate the time spent on the question."""
    if 'question_start_time' in request.session:
        start_time = datetime.datetime.strptime(request.session['question_start_time'], '%Y-%m-%d %H:%M:%S.%f')
        time_on_question = str((time_now - start_time).total_seconds())
        del request.session['question_start_time']
        return time_on_question
    return None

def extract_image_id(path):
    """Extract formatted image ID from full path."""
    parts = path.split('/', 2)  # Get the part after 'img/SBIs/'
    return parts[2] if len(parts) >= 3 else path

def process_heatmap_data(form, user_answer):
    """Process and clean heatmap data."""
    heatmap_raw = form.cleaned_data.get('heatmapFill', '[]')
    try:
        heatmap_list = json.loads(heatmap_raw)
        if "FORM" in heatmap_list:
            heatmap_list.remove("FORM")

        # The heatmap data is for the selected image, not necessarily the left image
        # The frontend already sends the correct heatmap data for the selected image
        selected_heatmap = heatmap_list
        unselected_heatmap = []
        return selected_heatmap, unselected_heatmap
    except Exception as e:
        print("Heatmap parsing error:", e)
        return [], []

def create_response_instance(form, request, ppant_instance, selected_image, time_now, time_on_question):
    """Create and save response entry."""
    user_answer = form.cleaned_data['choice']
    confidence = form.cleaned_data['confidence']
    inconsistency_types = form.cleaned_data.get('inconsistency_type', [])

    # Generate a unique response_id
    import uuid
    response_id = str(uuid.uuid4())[:20]  # Limit to 20 chars as per model definition

    fake_on_left = request.session.get('fake_on_left', False)
    correct_answer = 'left' if fake_on_left else 'right'
    is_correct = (user_answer == correct_answer)

    real_path = selected_image.real_path
    fake_path = selected_image.fake_path

    left_path = fake_path if fake_on_left else real_path
    right_path = real_path if fake_on_left else fake_path

    left_image_id = extract_image_id(left_path)
    right_image_id = extract_image_id(right_path)

    selected_path = left_path if user_answer == 'left' else right_path
    unselected_path = right_path if user_answer == 'left' else left_path

    selected_image_id = extract_image_id(selected_path)
    unselected_image_id = extract_image_id(unselected_path)

    selected_heatmap, unselected_heatmap = process_heatmap_data(form, user_answer)

    selected_gt = 1 if 'fake' in selected_image_id else 0
    unselected_gt = 0 if selected_gt == 1 else 1

    responses = []
    for image_id, heatmap, is_selected, gt in [
        (selected_image_id, selected_heatmap, True, selected_gt),
        (unselected_image_id, unselected_heatmap, False, unselected_gt)
    ]:
        assigned_label = 1 if is_selected else 0
        position = 'left' if (user_answer == 'left' and is_selected) or (user_answer == 'right' and not is_selected) else 'right'

        # For the unselected image, set all inconsistency types to 0
        if is_selected:
            response = Response(
                ppant_id=ppant_instance,
                time_at_submission=time_now,
                time_on_question=time_on_question,
                response_id=response_id,  # Add the response_id
                image_id=image_id,
                choice=user_answer,
                confidence=confidence,
                heatmapFill=heatmap,
                assigned_label=assigned_label,
                gt=gt,
                inconsistency_boundary=int('boundary' in inconsistency_types),
                inconsistency_color=int('color' in inconsistency_types),
                inconsistency_geometry=int('geometry' in inconsistency_types),
                inconsistency_landmark=int('landmark' in inconsistency_types),
                inconsistency_texture=int('texture' in inconsistency_types),
                position=position,
                is_correct=is_correct  # mark correct only for selected
            )
        else:
            # For unselected image, all inconsistency types are 0
            response = Response(
                ppant_id=ppant_instance,
                time_at_submission=time_now,
                time_on_question=time_on_question,
                response_id=response_id,  # Add the response_id
                image_id=image_id,
                choice=user_answer,
                confidence=confidence,
                heatmapFill=heatmap,
                assigned_label=assigned_label,
                gt=gt,
                inconsistency_boundary=0,
                inconsistency_color=0,
                inconsistency_geometry=0,
                inconsistency_landmark=0,
                inconsistency_texture=0,
                position=position,
                is_correct=False
            )
        response.save()
        responses.append(response)

    return responses

@ensure_csrf_cookie
def mainQuPage(request):
    """Main page with the image task."""
    time_now = datetime.datetime.now()
    how_many_qus = 20

    if 'question_start_time' not in request.session:
        request.session['question_start_time'] = time_now.strftime('%Y-%m-%d %H:%M:%S.%f')
        request.session.save()

    ppant_instance = get_participant(request)
    if ppant_instance is None:
        return redirect('intro')

    img_nums_so_far_this_ppant, correct_answers_count = get_participant_responses(ppant_instance)

    survey_completion_result = check_survey_completion(
        request, img_nums_so_far_this_ppant, correct_answers_count, how_many_qus
    )
    if survey_completion_result:
        return survey_completion_result

    all_images = Image.objects.all().order_by('times_seen')

    if request.method == 'POST':
        form = SubmitResponse(request.POST)
        if form.is_valid():
            time_on_question = calculate_time_on_question(request, time_now)

            try:
                selected_image = Image.objects.get(id=form.cleaned_data['image'])
            except Image.DoesNotExist:
                return JsonResponse({'error': 'Image not found'}, status=400)

            create_response_instance(
                form, request, ppant_instance, selected_image,
                time_now, time_on_question
            )

            # Clear session
            clear_session_data(request)

            return JsonResponse({
                'is_correct': form.cleaned_data['choice'] == request.session.get('correct_answer', 'left'),
                'correct_answer': request.session.get('correct_answer', 'left')
            })
        else:
            return JsonResponse({'error': 'Form is invalid', 'errors': form.errors.as_json()}, status=400)

    else:
        form = SubmitResponse()

    # GET: set up new question
    selected_image = select_image(request, all_images)
    left_image_path, right_image_path, correct_answer = determine_image_placement(request, selected_image)

    context = prepare_context(
        request, selected_image, left_image_path, right_image_path,
        img_nums_so_far_this_ppant, correct_answers_count, how_many_qus,
        form
    )

    return render(request, 'page1.html', context)
