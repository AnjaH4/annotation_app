import datetime
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
        return redirect(exampleTask)

    return render(request, 'entrancePage.html', context=context)


def consent(request):
    form = InformedConsent()

    context = {
        'form': form,
        'ppant_id': request.session.get('ppant_id', 'default'),
    }

    if request.method == 'POST':
        return redirect(bonusPaymentInfo)

    return render(request, 'consent.html', context=context)  #to runa in vzame consent.html template za form


def bonusPaymentInfo(request):
    category = request.session.get('category', 'default')
    if request.method == 'POST':
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
        # All users get the same experience with 'help' advice type
        advice_time_instance = AdviceStartTime(
            ppant_id=ppant_instance,
            advice_type='help',  # Fixed advice type for all users
            time_at_submission=time_now
        )
        advice_time_instance.save()
        print(category)
        # Direct all users to the helpPage, which shows inconsistencies
        return redirect(helpPage)

    return render(request, 'bonusPaymentInfo.html')


def taskInstructions(request):
    return render(request, 'taskInstructions.html')


def exampleTask(request):
    context = {
        'category': request.session.get('category', 'default'),
    }
    return render(request, 'exampleTask.html', context=context)


def dataProtection(request):
    return render(request, 'dataProtection.html')


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
    maj = ['a', 'b', 'c']
    random.shuffle(maj)
    minA = ['1', '2', '3']
    random.shuffle(minA)
    minB = ['1', '2', '3', '4']
    random.shuffle(minB)
    minC = ['1', '2', '3']
    random.shuffle(minC)

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
        return redirect(mainQuPage)

    context = {
        'maj': maj,
        'minA': minA,
        'minB': minB,
        'minC': minC,
    }
    return render(request, 'introhelp.html', context=context)


def greetingQu(request):  #tega ne rabim
    form = Greetings()
    form_thanks = Thanks()
    context = {
        'form': form,
        'form_thanks': form_thanks,
    }
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
            ppant_id = ppant_instance,
            advice_type = 'control',
            time_at_submission = time_now
        )
        advice_time_instance.save()
        return redirect(mainQuPage)
    return render(request, 'greetingQu.html', context=context)


@ensure_csrf_cookie
def submit_answer(request):
    """Handle AJAX form submissions and return feedback as JSON"""
    if request.method == 'POST':
        form = SubmitResponse(request.POST)

        if form.is_valid():
            time_now = datetime.datetime.now()
            this_ppant_id = request.session.get('ppant_id', 'default')
            ppant_query = Participant.objects.filter(ppant_id=this_ppant_id)

            # Initialize ppant_instance to None
            ppant_instance = None

            # Try to get the participant instance
            for i in ppant_query:
                ppant_instance = i
                break

            # If no participant found, return an error
            if ppant_instance is None:
                return JsonResponse({'error': 'Participant not found'}, status=400)

            # Get image ID and correct answer from session
            img_this = form.cleaned_data['image']
            img_full_id = 'image'+str(img_this)

            # Get the correct answer from session
            correct_answer = request.session.get('correct_answer', 'left')
            user_answer = form.cleaned_data['choice']

            # Check if user's answer is correct
            is_correct = (user_answer == correct_answer)

            # Generate unique response ID
            resp_rand = random.randint(0, 99999) + 1
            try:
                resps = Response.objects.all()
                while resp_rand in [r.response_id for r in resps]:
                    resp_rand = random.randint(0, 99999) + 1
            except:
                print("something went wrong with response table")

            # Save response
            response_instance = Response(
                time_at_submission=time_now,
                response_id=resp_rand,
                ppant_id=ppant_instance,
                image_id=img_full_id,
                choice=form.cleaned_data['choice'],
                confidence=form.cleaned_data['confidence'],
                inconsistency_type=','.join(form.cleaned_data['inconsistency_type']),
                reasoning="",  # Reasoning field has been removed from the form
                heatmapFill=form.cleaned_data['heatmapFill'],
                is_correct=is_correct,
            )
            response_instance.save()

            # Return feedback as JSON
            return JsonResponse({
                'is_correct': is_correct,
                'correct_answer': correct_answer
            })
        else:
            print("Form errors:", form.errors)
            return JsonResponse({'error': 'Form is invalid', 'errors': form.errors.as_json()}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@ensure_csrf_cookie
def mainQuPage(request): #stran z vprašanjem
    time_now = datetime.datetime.now()
    print("MAINQUPAGE")
    how_many_qus = 20   #nastavi št vprašanj

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

    img_nums_so_far_this_ppant = []
    correct_answers_count = 0

    try:
        responses_by_this_ppant = Response.objects.filter(ppant_id=ppant_instance)
        for j in responses_by_this_ppant:
            img_num = str(j.image_id)[5:]  # da dobimo samo številko slike
            img_nums_so_far_this_ppant += [img_num]
            if j.is_correct:
                correct_answers_count += 1
    except:
        print("something failed in response table...")

    print("This ppant has seen these imgs:",img_nums_so_far_this_ppant)
    print("Ppant", this_ppant_id, "has so far completed", len(img_nums_so_far_this_ppant), "questions.")
    print("Ppant", this_ppant_id, "has", correct_answers_count, "correct answers so far.")

    # AFTER ALL QUESTIONS COMPLETE, END SURVEY.
    if len(img_nums_so_far_this_ppant) > (how_many_qus-1):
    # if len(img_nums_so_far_this_ppant) > 1:
        # Calculate accuracy percentage
        accuracy_percentage = (correct_answers_count / how_many_qus) * 100

        # Determine achievement level based on accuracy
        achievement = "Beginner"
        if accuracy_percentage >= 90:
            achievement = "Expert"
        elif accuracy_percentage >= 80:
            achievement = "Advanced"
        elif accuracy_percentage >= 70:
            achievement = "Intermediate"
        elif accuracy_percentage >= 50:
            achievement = "Novice"
        else:
            achievement = "Fool"

        # Pass results to the template
        context = {
            'correct_answers_count': correct_answers_count,
            'total_questions': how_many_qus,
            'accuracy_percentage': accuracy_percentage,
            'achievement': achievement,
            'ppant_id': this_ppant_id,
            'category': request.session.get('category', 'default'),
        }
        return render(request, 'endsurvey.html', context)

    # Get all images and sort by times_seen (ascending)
    all_images = Image.objects.all().order_by('times_seen')

    # Process form submission
    print("any POST:")
    print(request.POST)
    if request.method == 'POST':
        print("POSTING")
        form = SubmitResponse(request.POST)

        if form.is_valid():
            print("FORM VALID")
            this_ppant_id = request.session.get('ppant_id', 'default')
            ppant_query = Participant.objects.filter(ppant_id= this_ppant_id)

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

            # Get image ID and correct answer from session
            img_this = form.cleaned_data['image']
            img_full_id = 'image'+str(img_this)
            print(img_full_id)

            # Get the correct answer from session
            correct_answer = request.session.get('correct_answer', 'left')
            user_answer = form.cleaned_data['choice']

            # Check if user's answer is correct
            is_correct = (user_answer == correct_answer)

            # Generate unique response ID
            resp_rand = random.randint(0, 99999) + 1
            try:
                resps = Response.objects.all()
                while resp_rand in [r.response_id for r in resps]:
                    resp_rand = random.randint(0, 99999) + 1
            except:
                print("something went wrong with response table")

            # Save response
            response_instance = Response(
                time_at_submission=time_now,
                response_id = resp_rand,
                ppant_id = ppant_instance,
                image_id = img_full_id,
                choice = form.cleaned_data['choice'],
                confidence = form.cleaned_data['confidence'],
                inconsistency_type = ','.join(form.cleaned_data['inconsistency_type']),
                reasoning = "",  # Reasoning field has been removed from the form
                heatmapFill = form.cleaned_data['heatmapFill'],
                is_correct = is_correct,
            )
            response_instance.save()

            # Store feedback in session for display on next page
            request.session['feedback'] = {
                'is_correct': is_correct,
                'correct_answer': correct_answer
            }
            request.session.save()  # Ensure session is saved

            return HttpResponseRedirect(reverse('main1'))
        else:
            print("FORM INVALID")
    else:
        print("GET request.")
        form = SubmitResponse()

    # Select the image pair that has been shown the least number of times
    # If multiple pairs have the same count, select a random one from the least shown images
    selected_image = None

    if all_images.exists():
        # Get the minimum times_seen count
        min_times_seen = all_images.first().times_seen

        # Get all images with the minimum times_seen count
        least_shown_images = all_images.filter(times_seen=min_times_seen)

        # Select a random image from the least shown images
        # If there's only one image with the minimum count, it will select that one
        selected_image = random.choice(list(least_shown_images))

        # Increment the times_seen counter
        selected_image.times_seen += 1
        selected_image.save()
    else:
        # If no images exist, create a default one (this should not happen in production)
        print("No images found in database!")
        # You might want to handle this case differently

    # Randomly decide which side (left or right) will show the fake image
    fake_on_left = random.choice([True, False])
    correct_answer = 'left' if fake_on_left else 'right'

    # Store the correct answer in the session for validation when the form is submitted
    request.session['correct_answer'] = correct_answer
    request.session.save()  # Ensure session is saved after setting correct_answer

    # Prepare paths for real and fake images
    real_path = None
    fake_path = None

    if selected_image:
        # Extract directory and filename from image_id (e.g., "065_0")
        image_id = selected_image.image_id

        # Use the paths stored in the database
        real_path = selected_image.real_path
        fake_path = selected_image.fake_path

        # Log the paths for debugging
        print(f"Real path: {real_path}")
        print(f"Fake path: {fake_path}")

    # Determine which image goes on which side
    left_image_path = fake_path if fake_on_left else real_path
    right_image_path = real_path if fake_on_left else fake_path

    # Removed telltale signs variables

    # Get feedback from previous question if available
    feedback = request.session.get('feedback', None)

    # Calculate questions attempted and current question number
    questions_attempted = len(img_nums_so_far_this_ppant)
    current_question_number = questions_attempted + 1


    context = {
        'category': request.session.get('category', 'default'),
        'numsYet': request.session.get('numsYet', 'default'),
        'num': selected_image.id if selected_image else 0,
        'form': form,
        'ppant_id': request.session.get('ppant_id', 'default'),
        'left_image_path': left_image_path,
        'right_image_path': right_image_path,
        'feedback': feedback,
        'correct_answers_count': correct_answers_count,
        'total_questions': how_many_qus,
        'questions_attempted': questions_attempted,
        'current_question_number': current_question_number,
    }

    return render(request, 'page1.html', context=context)
