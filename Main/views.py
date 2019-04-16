from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.http import HttpResponse
from . forms import CreateAccountForm, UpdateAccountForm, CreateJobForm, ListJobsForm, GenerateReportForm, ListJobsCreator, ListJobsSeekers, GenerateReviewForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from . models import Profile, Post, Seeker, Creator, Report, SeekerReview, CreatorReview
from django.core.mail import EmailMessage, send_mail
from django.core.exceptions import ValidationError
from django.template import loader #?
from django.db.models import Q #for Django OR filters
from django.db.models.fields import BLANK_CHOICE_DASH
from . models import locations
from math import sin, cos, sqrt, atan2, radians

from django.utils.timezone import datetime

def create_account(request):
    if request.method == "POST": #user clicks register button
        #print('create account post')
        form = CreateAccountForm(request.POST)

        if form.is_valid():
            #print('Create Account Valid')

            #get form data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']

            #create and add user to database
            user = User.objects.create(username=username, email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            Profile.objects.create(User=user, Age=age)
            Seeker.objects.create(User=user)
            Creator.objects.create(User=user)

            user.save()

            login(request, user)
            return redirect('/home_seeker/')

        else:
            pass
            #print("Create Account not Valid")

    else: #user is viewing the create account page
        #print("Load Create Account")
        form = CreateAccountForm()

    return render(request, 'createAccount.html', {'form':form})

def profile(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    if request.GET.get('username'): #the .get() needs to be used to stop error if username is null
        username = request.GET['username']
        user = User.objects.filter(username=username).first() #assume there is only one object
        
        createReview = CreatorReview.objects.filter(User=user)
        creatorScore = 0
        counterCreator = 0
        for review in createReview:
            creatorScore += review.Rating
            counterCreator += 1
        if (counterCreator == 0):
            creatorScore = -1
        else:
            creatorScore = creatorScore / counterCreator

        seekReview = SeekerReview.objects.filter(User=user)
        seekerScore = 0
        counterSeeker = 0
        for review in seekReview:
            seekerScore += review.Rating
            counterSeeker += 1
        if (counterSeeker == 0):
            seekerScore = -1
        else:
            seekerScore = seekerScore / counterSeeker
        
        #print("creatorScore:", creatorScore)
        #print("seekerScore:", seekerScore)

        if user:
            num_reports = Report.objects.filter(User=user).count()
            return render(request, 'profile.html', {'user_info':user, 'num_reports':num_reports, 'creatorScore':creatorScore, 'seekerScore':seekerScore})

    return render(request, 'profile.html')

def update_account(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == 'POST':
        print('update account post')
        form = UpdateAccountForm(request.user, request.POST, request.FILES)
        print(form.errors)

        if form.is_valid():
            print('update account valid')
            update_all = 'update_all_button' in request.POST

            if form.cleaned_data['profile_picture'] and ('profile_picture_button' in request.POST or update_all):
                request.user.profile.Portrait = form.cleaned_data['profile_picture']  

            if form.cleaned_data['first_name'] and ('first_name_button' in request.POST or update_all):
                request.user.first_name = form.cleaned_data['first_name']

            if  form.cleaned_data['last_name'] and ('last_name_button' in request.POST or update_all):
                request.user.last_name = form.cleaned_data['last_name']

            if form.cleaned_data['age'] and ('age_button' in request.POST or update_all):
                request.user.profile.Age = form.cleaned_data['age']

            if form.cleaned_data['email'] and ('email_button' in request.POST or update_all):
                request.user.email = form.cleaned_data['email']

            if form.cleaned_data['description'] and ('description_button' in request.POST or update_all):
                request.user.profile.Description = form.cleaned_data['description']
            
            print(form.cleaned_data['pref_job_type'])
            print('pref_job_type_button' in request.POST)
            if (form.cleaned_data['pref_job_type'] != '') and ('pref_job_type_button' in request.POST or update_all):
                request.user.seeker.PrefType = form.cleaned_data['pref_job_type']

            if (form.cleaned_data['zip_code']) and ('zip_code_button' in request.POST or update_all):
                request.user.profile.ZipCode = form.cleaned_data['zip_code']

            if (form.cleaned_data['password'] and form.cleaned_data['password_confirmation']) and ('password_button' in request.POST or update_all):
                request.user.set_password(form.cleaned_data['password'])

            request.user.save()
            request.user.profile.save()
            request.user.seeker.save()

            return render(request, 'updateAccount.html', {'form': form, 'user_info':request.user})
    else:
        form = UpdateAccountForm(request.user)

    return render(request, 'updateAccount.html', {'form': form, 'user_info':request.user})

	#reset password
def reset_password(request):
	return render(request, 'reset_password.html')
	
def reset_instructions(request):
	return render(request, 'reset_instructions.html')
	
def new_password(request):
	return render(request, 'new_password.html')
	
def reset_success(request):
	return render(request, 'reset_success.html')
	
#home pages
def home_creator(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    return render(request, 'home_creator.html')
	
def home_seeker(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    print("isNotified", request.user.profile.isNotified)
    return render(request, 'home_seeker.html')

def login_request(request):
    if request.method == 'POST':
        print('login post')
        form = AuthenticationForm(request=request, data=request.POST)

        if form.is_valid():
            print('login valid')
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                #print('login success')
                login(request, user)
                return redirect('/home_seeker/')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form':form})

#redirect to home    
def logout_request(request):
    logout(request)
    return redirect('/login/')

#create_job page
def create_job(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == 'POST':
        print('create job post')
        form = CreateJobForm(request.POST)

        print(form.errors)

        if form.is_valid():
            print('create job valid')

            #get form fields
            pay = form.cleaned_data['pay']
            date = form.cleaned_data['date_time']
            description = form.cleaned_data['description']
            job_type = form.cleaned_data['job_type']
            zip_code = form.cleaned_data['zip_code']

            #create new job
            post = Post.objects.create(Pay=pay, DateTime=date, Description=description, JobType=job_type, ZipCode=zip_code, userID=request.user.id, userName=request.user.username)
            request.user.creator.Posts.add(post)

            return redirect('/add_job/')
    else:
        form = CreateJobForm()

    return render(request, 'Jobs/bigBoxJob.html', {'form':form})

def list_job(request):
    print('list job')

    expired = Post.objects.filter(DateTime__lt=datetime.now(),)
    expired.update(Active=1)

    if not request.user.is_authenticated:
        print('list job not authenticated')
        return redirect('/login/')

    if request.method == "GET":
        print('list job get')
        form = ListJobsForm(request.GET)

        if form.is_valid():
            print('list job valid')
            job_type = form.cleaned_data['job_type']
            min_wage = form.cleaned_data['min_wage']
            max_wage = form.cleaned_data['max_wage']
            if (job_type != 'FF'):
                if (job_type != '' and min_wage and max_wage): #all inputs filled in
                    print('all inputs')
                    jobs = Post.objects.filter(JobType=job_type, Pay__range=[min_wage, max_wage])
                elif (job_type == '' and not min_wage and not max_wage): #no inputs filled in
                    print('no inputs')
                    jobs = Post.objects.all()
                else: #mixed inputs filled in
                    print('mixed inputs')
                    if min_wage and not max_wage:
                        jobs = Post.objects.filter(Q(JobType=job_type) | Q(Pay__gte=min_wage))
                    elif not min_wage and max_wage:
                        jobs = Post.objects.filter(Q(JobType=job_type) | Q(Pay__lte=max_wage))
                    else:
                        jobs = Post.objects.filter(Q(JobType=job_type) | Q(Pay__range=[min_wage, max_wage]))
            else: 
                job_pref = request.user.seeker.PrefType
                print(job_pref)
                jobs = Post.objects.filter(Q(JobType=job_pref))
        else:
            jobs = Post.objects.all()
    else:
        jobs = Post.objects.all()
        form = ListJobsForm()

    #Exclude Users Own Jobs
    for job in jobs:
        if (job.userID == request.user.id):
            jobs = jobs.exclude(id = job.id)

    #sort by distance, then pay, then date
    jobs = jobs.filter(Active=0)
    jobs = jobs.order_by('Pay', 'DateTime')
    if (request.user.profile.ZipCode != None):
        jobs = sorted(jobs, key = lambda job : distBetween(job.ZipCode, request.user.profile.ZipCode))

    return render(request, 'Jobs/listJobs.html', {'form':form, 'jobs':jobs})

def new_job(request): #need to change this so it shows that job info !!!
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    return render(request, 'Jobs/viewNewJob.html')

def one_job_seeker(request, jobID): #yeehaw im making progress
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    jobs = Post.objects.filter(id=jobID)
    return render(request, 'Jobs/oneJob.html', {'jobs':jobs})

#Job Creator Pages
def reopen_job(request, post_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    if post_id is not None:
        post = Post.objects.filter(id=post_id).first()
        if post is not None:
            post.Active = 0 #open
            post.Interested.clear()
            #reset chosen seeker
            post.save()          

    return redirect('/past_jobs_creator/')

def all_jobs_creator(request, job):
    expired = request.user.creator.Posts.filter(DateTime__lt=datetime.now())
    expired.update(Active=1)

    if not request.user.is_authenticated:
        return redirect('/login/')
        
    if(request.GET.get('all_jobs')):
        print("all_jobs button")
        form = ListJobsCreator(request.GET)

        if (job != "all_jobs"):
            return redirect('/all_jobs_creator/all_jobs/?all_jobs=all_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
            
        typeOfJob = "all_jobs"
        job="all_jobs"
        active = -1
    elif(request.GET.get("accepted_jobs")):
        print("accepted_jobs button")

        if (job != "accepted_jobs"):
            return redirect('/all_jobs_creator/accepted_jobs/?accepted_jobs=accepted_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')

        typeOfJob = "accepted_jobs"
        job="accepted_jobs"
        active = 2
    elif(request.GET.get("pending_jobs")):
        print("pending_jobs button")
        
        if (job != "pending_jobs"):
            return redirect('/all_jobs_creator/pending_jobs/?pending_jobs=pending_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')

        typeOfJob = "pending_jobs"
        job="pending_jobs"
        active = 0

    elif(request.GET.get("past_jobs")):
        print("past_jobs button")
        
        if (job != "past_jobs"):
            return redirect('/all_jobs_creator/past_jobs/?past_jobs=past_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')

        typeOfJob = "past_jobs"
        job="past_jobs"
        active = 1
    elif(request.GET.get("apply")):
        print("Apply")
        
        typeOfJob = job
        if (job=="all_jobs"):
            active = -1
        elif (job=="accepted_jobs"):
            active = 2
        elif (job=="pending_jobs"):
            active = 0
        else:
            active = 1
    elif(request.GET.get("reset")):
        print("Reset")

        typeOfJob = job
        if (job=="all_jobs"):
            return redirect('/all_jobs_creator/all_jobs/?all_jobs=all_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
        elif (job=="accepted_jobs"):
            return redirect('/all_jobs_creator/accepted_jobs/?accepted=accepted_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
        elif (job=="pending_jobs"):
            return redirect('/all_jobs_creator/pending_jobs/?pending_jobs=pending_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
        else:
            return redirect('/all_jobs_creator/past_jobs/?past_jobs=past_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
    else:
        print("else")
        typeOfJob = job
        job = "all_jobs"
        active = -1
    
    if (typeOfJob == "all_jobs"):
        jobs = request.user.creator.Posts.all()
    elif (typeOfJob == "accepted_jobs"):
        jobs = request.user.creator.Posts.filter(Active=2)
    elif (typeOfJob == "pending_jobs"):
        jobs = request.user.creator.Posts.filter(Active=0)
    else:
        jobs = request.user.creator.Posts.filter(Active=1)

    print(jobs)

    if request.method == "GET":
        form = ListJobsCreator(request.GET)
        if form.is_valid():
            job_type = form.cleaned_data['job_type']
            min_wage = form.cleaned_data['min_wage']
            max_wage = form.cleaned_data['max_wage']
            search = form.cleaned_data['search']
                
            if (job_type != '' and min_wage and max_wage): #all inputs filled in
                jobs = jobs.filter(Description__icontains=search, JobType=job_type, Pay__range=[min_wage, max_wage])
            elif (job_type == '' and not min_wage and not max_wage): #no inputs filled in
                jobs = jobs.filter(Description__icontains=search)             
            else: #mixed inputs filled in
                if min_wage and not max_wage:
                    jobs = jobs.filter(Q(Description__icontains=search), Q(JobType=job_type) | Q(Pay__gte=min_wage))
                elif not min_wage and max_wage:
                    jobs = jobs.filter(Q(Description__icontains=search),  Q(JobType=job_type) | Q(Pay__lte=max_wage))
                else:
                    jobs = jobs.filter(Q(Description__icontains=search),  Q(JobType=job_type) | Q(Pay__range=[min_wage, max_wage]))

            print(jobs)
        else:
            jobs = jobs.all()
    else:
        jobs = jobs.all()
        form = ListJobsCreator()
    
    jobs = jobs.order_by('Pay', 'DateTime')

    return render(request, 'Creator/allJobsCreator.html', {'form':form, 'jobs':jobs, 'typeOfJob':typeOfJob}, job)

def delete_job(request, deletedJobID):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    job = Post.objects.filter(id=deletedJobID).first()
    job.delete()
    return redirect('/all_jobs_creator/all_jobs/')

def accepted_jobs_creator(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    return render(request, 'Creator/acceptedJobsCreator.html')

def pending_jobs_creator(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    if request.method == "GET":
        print('creator job get')
        form = ListJobsForm(request.GET)

        if form.is_valid():
            print('list job valid')

            #max_distance = form.cleaned_data['max_distance']
            job_type = form.cleaned_data['job_type']
            min_wage = form.cleaned_data['min_wage']
            max_wage = form.cleaned_data['max_wage']

            if (job_type != '' and min_wage and max_wage): #all inputs filled in
                jobs = request.user.creator.Posts.filter(JobType=job_type, Pay__range=[min_wage, max_wage])
            elif (job_type == '' and not min_wage and not max_wage): #no inputs filled in
                jobs = request.user.creator.Posts.all()
            else: #mixed inputs filled in
                if min_wage and not max_wage:
                    jobs = request.user.creator.Posts.filter(Q(JobType=job_type) | Q(Pay__gte=min_wage))
                elif not min_wage and max_wage:
                    jobs = request.user.creator.Posts.filter(Q(JobType=job_type) | Q(Pay__lte=max_wage))
                else:
                    jobs = request.user.creator.Posts.filter(Q(JobType=job_type) | Q(Pay__range=[min_wage, max_wage]))
        else:
            jobs = request.user.creator.Posts.all()
    else:
        jobs = request.user.creator.Posts.all()
        form = ListJobsForm()

    jobs = jobs.order_by('Pay', 'DateTime')
    return render(request, 'Creator/pendingJobsCreator.html', {'form':form, 'jobs':jobs}) #'typeOfJob':typeOfJob})

def past_jobs_creator(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    return render(request, 'Creator/pastJobsCreator.html')

def one_job_creator(request, job_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    post = Post.objects.filter(id=job_id).first()
    if post == None:
        return render(request, 'Jobs/oneJob.html')

    interested_seekers = post.Interested.all()
    return render(request, 'Jobs/creatorOneJob.html', {'post':post, 'interested_seekers':interested_seekers})

def seeker_one_job(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    return render(request, 'Jobs/oneJob.html')

#Jobs Seeker Pages
def all_jobs_seeker(request, job):
    expired = Post.objects.filter(DateTime__lt=datetime.now(),)
    expired.update(Active=1)

    if not request.user.is_authenticated:
        return redirect('/login/')
        
    if(request.GET.get('all_jobs')):
        print("all_jobs button")
        form = ListJobsSeekers(request.GET)

        if (job != "all_jobs"):
            return redirect('/all_jobs_seeker/all_jobs/?all_jobs=all_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
            
        typeOfJob = "all_jobs"
        job="all_jobs"
        active = -1
    elif(request.GET.get("accepted_jobs")):
        print("accepted_jobs button")

        if (job != "accepted_jobs"):
            return redirect('/all_jobs_seeker/accepted_jobs/?accepted_jobs=accepted_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')

        typeOfJob = "accepted_jobs"
        job="accepted_jobs"
        active = 2
    elif(request.GET.get("interested_jobs")):
        print("interested_jobs button")
        
        if (job != "interested_jobs"):
            return redirect('/all_jobs_seeker/interested_jobs/?interested_jobs=interested_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')

        typeOfJob = "interested_jobs"
        job="interested_jobs"
        active = 0

    elif(request.GET.get("past_jobs")):
        print("past_jobs button")
        
        if (job != "past_jobs"):
            return redirect('/all_jobs_seeker/past_jobs/?past_jobs=past_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')

        typeOfJob = "past_jobs"
        job="past_jobs"
        active = 1
    elif(request.GET.get("apply")):
        print("Apply")
        
        typeOfJob = job
        if (job=="all_jobs"):
            active = -1
        elif (job=="accepted_jobs"):
            active = 2
        elif (job=="interested_jobs"):
            active = 0
        else:
            active = 1
    elif(request.GET.get("reset")):
        print("Reset")

        typeOfJob = job
        if (job=="all_jobs"):
            return redirect('/all_jobs_seeker/all_jobs/?all_jobs=all_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
        elif (job=="accepted_jobs"):
            return redirect('/all_jobs_seeker/accepted_jobs/?accepted=accepted_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
        elif (job=="interested_jobs"):
            return redirect('/all_jobs_seeker/interested_jobs/?interested_jobs=interested_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
        else:
            return redirect('/all_jobs_seeker/past_jobs/?past_jobs=past_jobs&max_distance=&job_type=&min_wage=&max_wage=&search=&')
    else:
        print("else")
        typeOfJob = job
        job = "all_jobs"
        active = -1
    #jobs.request.user
    #.InterestedSeeker.a;
    #jobs = request.user.interested_seekers
    #jobs = Post.objects.filter(Interested=request.user)
    #print("jobs", jobs)
    
    if (typeOfJob == "all_jobs"):
        jobs = request.user.interested_seekers
        #print("here", request.user.profile.isNotified)
        print("Before", request.user.profile.isNotified)
        profile = request.user.profile
        profile.isNotified = False
        profile.save()
        #t.save(['value'])

        #User.objects.get(id=request.user.id).profile.isNotified = True
        print("After", request.user.profile.isNotified)
    elif (typeOfJob == "accepted_jobs"):
        jobs = request.user.interested_seekers.filter(Chosen=request.user, Active=2)
        profile = request.user.profile
        profile.isNotified = False
        profile.save()
    elif (typeOfJob == "interested_jobs"):
        jobs = request.user.interested_seekers.filter(Active=0)
    else:
        jobs = request.user.interested_seekers.filter(Active=1)

    if request.method == "GET":
        form = ListJobsSeekers(request.GET)
        if form.is_valid():
            zip_code = form.cleaned_data['zip_code']
            job_type = form.cleaned_data['job_type']
            min_wage = form.cleaned_data['min_wage']
            max_wage = form.cleaned_data['max_wage']
            search = form.cleaned_data['search']
            
            if (job_type != '' and min_wage and max_wage): #all inputs filled in
                jobs = jobs.filter(Description__icontains=search, JobType=job_type, Pay__range=[min_wage, max_wage])
            elif (job_type == '' and not min_wage and not max_wage): #no inputs filled in
                jobs = jobs.filter(Description__icontains=search)             
            else: #mixed inputs filled in
                if min_wage and not max_wage:
                    jobs = jobs.filter(Q(Description__icontains=search), Q(JobType=job_type) | Q(Pay__gte=min_wage))
                elif not min_wage and max_wage:
                    jobs = jobs.filter(Q(Description__icontains=search),  Q(JobType=job_type) | Q(Pay__lte=max_wage))
                else:
                    jobs = jobs.filter(Q(Description__icontains=search),  Q(JobType=job_type) | Q(Pay__range=[min_wage, max_wage]))
                
            if (zip_code): #ZipCode Exists
                    for job in jobs:
                        distance = distBetween(job.ZipCode, request.user.profile.ZipCode)
                        if (distance > zip_code):
                            jobs = jobs.exclude(id = job.id)
            
        else:
            jobs = jobs.all()
    else:
        jobs = jobs.all()
        form = ListJobsSeekers()

    jobs = jobs.order_by('Pay', 'DateTime')
    return render(request, 'Seeker/allJobsSeeker.html', {'form':form, 'jobs':jobs, 'typeOfJob':typeOfJob}, job)

def accepted_jobs_seeker(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
        
    return render(request, 'Seeker/acceptedJobsSeeker.html')

def interested_jobs_seeker(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    return render(request, 'Seeker/interestedJobsSeeker.html')
	
#User Report Page
def generate_report(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    #check get info
    if request.GET.get('username'):
        username = request.GET.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, 'generate_report.html') #no form info should be displayed, it isn't needed in this case
    else:
        return render(request, 'generate_report.html')

    #process request
    if request.method == "POST":
        #print('create report post')
        form = GenerateReportForm(request.POST)

        if form.is_valid():
            #print('create report valid')
            classification = form.cleaned_data['classification']
            details = form.cleaned_data['details']
            Report.objects.create(Classification=classification, Details=details, User=user)

            return redirect('/profile/?username=' + user.username)
    else:
        form = GenerateReportForm()

    return render(request, 'generate_report.html', {'form':form, 'user_info':user})

def generate_review(request, user_id, is_seeker):
    #if is_seeker is 0 the user is being reviewed as a creator
    #if is_seeker is 1 the user is being reviewed as a seeker

    if not request.user.is_authenticated:
        print('not logged in')
        return redirect('/login/')

    if request.method == "POST":
        print('generate review post')
        form = GenerateReviewForm(request.POST)

        #process params
        user = User.objects.filter(id=user_id).first()

        if user == None or is_seeker == None:
            form.add_error(None, 'url information is incorrect')
            return render(request, 'generate_review.html', {'form':form})

        is_seeker = False if is_seeker == 0 else True

        if form.is_valid():
            print('generate review valid')
            rating = form.cleaned_data['rating']

            if is_seeker:
                SeekerReview.objects.create(Rating=rating, User=user)
            else:
                CreatorReview.objects.create(Rating=rating, User=user)

            return redirect('/home_seeker/')
        else:
            print(form.errors)
    else:
        form = GenerateReviewForm()

    return render(request, 'generate_review.html', {'form':form})
	
def past_jobs_seeker(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    return render(request, 'Seeker/pastJobsSeeker.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('accounts:view_profile'))
        else:
            return redirect(reverse('accounts:change_password'))
    else:
        form = PasswordChangeForm(user=request.user)

        args = {'form': form}
        return render(request, 'accounts/change_password.html', args)


#this takes the email as a param and uses it to look for the right user to see if the email is regisetered. 
#if it is not registered then it will return -1
#otherwise it will send an email with a link to where to change the password
def change_passwordBackend(email):
    try:
        obj = User.objects.get(email = email)

    except:
        return -1

    link = ""
    message = "To reset your password go to this link: "
    message += link #add link
    sendEmail("change email", "",email)


def sendEmail(subject, message, emailTo):
    try:
        email = EmailMessage(subject, message, to=[emailTo])
        num = email.send()
    except:
        return -1
    return 1

#get job from job id
#add seeker id to Interested field of appropriate job record
#get seeker from users table
#get their email
#compose a generic message lol
def show_interest(request, jobID, seekerID):
    job = Post.objects.filter(id=jobID).first()
    #do error checking !!!!!!!! yip yap like check if record already in Interested
    seeker = User.objects.filter(id=seekerID).first()
    job.Interested.add(seeker)
    content = seeker.first_name + " is interested in this job: " + job.Description + ". Please visit BigBox to accept or decline this seeker."
    creator = User.objects.filter(id=job.userID).first()
    #print("seekerID:")
    #print(seekerID)
    #print(jobID)
    #print(creator)
    email = creator.email
    #print(email)
    val = sendEmail("Congrats, a seeker is interested in your job", content, email)
    return render(request, 'Jobs/showInterest.html')    
  
#distance between 2 zip codes in miles
def distBetween(zip1, zip2):
    try:
        radius = 3958.8 #radius of the Earth in miles

        lat1 = radians(locations.loc[int(zip1)].latitude)
        long1 = radians(locations.loc[int(zip1)].longitude)
        lat2 = radians(locations.loc[int(zip2)].latitude)
        long2 = radians(locations.loc[int(zip2)].longitude)

        dlon = long2 - long1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return radius * c
    except (KeyError, ValueError, TypeError): #for bad zip codes
        return -1

#in Post, set chosen id to id of seeker
#in Post, set Active to some value im not sure
#in Interested, delete record with job id and seeker(user) id
#send email to seeker to notify them that they've been chosen
def hire_seeker(request, jobID, seekerID, employerID):
    seeker = User.objects.filter(id=seekerID).first()
    profile = User.objects.filter(id=seekerID).first().profile
    profile.isNotified = True
    profile.save()
    print("seeker isNotified", seeker.username, seeker.profile.isNotified)
    seekerEmail = seeker.email
    employer = User.objects.filter(id =employerID).first()
    employerEmail = employer.email
    job = Post.objects.filter(id = jobID).first()
    job.Interested.remove(seeker)
    job.Chosen = seeker
    job.Active = 2
    job.save()
    content = "You have been hired for this job: " + job.Description + ". Here is your employers contact information: \n" + employer.first_name + "\n" + employerEmail
    val = sendEmail("Congrats, you have been hired!", content, seekerEmail)
    return render(request, 'Jobs/hireSeeker.html') 
