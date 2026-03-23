import os
from django.conf import settings
from django.shortcuts import render
import joblib
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import precision_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE 

def Training(request):
    
    # Load dataset
    data_set = pd.read_csv('media/ClassSurvey.csv')

    # Encode the target column
    encoder = LabelEncoder()
    data_set['SocialMediaAddiction'] = encoder.fit_transform(data_set['SocialMediaAddiction'])


    # Select relevant columns
    columns = [
        'Whatsapp', 'Instagram', 'Snapchat', 'Telegram', 'Facebook', 'BeReal',
        'TikTok', 'WeChat', 'Twitter', 'Linkedin', 'Messages',
        'TotalSocialMediaScreenTime', 'Number of times opened (hourly intervals)',
        'SocialMediaAddiction'
    ]
    df = data_set[columns]

    # Impute missing values
    imputer = SimpleImputer(strategy='mean')
    df[columns] = imputer.fit_transform(df[columns])
    
    

    # Prepare features and target variable
    X = df.drop('SocialMediaAddiction', axis=1)
    y = df['SocialMediaAddiction']

    Addicted_notAddicted_count = df['SocialMediaAddiction'].value_counts()
# Assuming 'Yes' is represented as 1 and 'No' as 0 after encoding
    Addicted_count = Addicted_notAddicted_count.get(1, 0)  # Number of "Yes" values
    notAddicted_count = Addicted_notAddicted_count.get(0, 0)   # Number of "No" values
    print("before balanced")
    print(f"Addicted_count: {Addicted_count}, Not_Addicted_count: {notAddicted_count}")


    smote = SMOTE(random_state=42)
    X_balanced, y_balanced = smote.fit_resample(X, y)


    balanced_yes_no_count = pd.Series(y_balanced).value_counts()
    balanced_yes_count = balanced_yes_no_count.get(1, 0)
    balanced_no_count = balanced_yes_no_count.get(0, 0)
    
    print("After balanced")
    print(f"Addicted_count: {balanced_yes_count}, Not_Addicted_count: {balanced_no_count}")
  

    # Save the modified DataFrame to a new CSV file
    df.to_csv('media/Filtered_ClassSurvey.csv', index=False)


    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

    # Initialize and train the RandomForest model
    random_forest = RandomForestClassifier()
    random_forest.fit(X_train, y_train)

    # Make predictions
    y_pred = random_forest.predict(X_test)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)

      # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'confusion_matrix.png'))
    plt.close()
    
    
     # Feature importance
    feature_importances = random_forest.feature_importances_
    features = X.columns
    feature_df = pd.DataFrame({'Features': features, 'Importance': feature_importances})
    feature_df = feature_df.sort_values(by='Importance', ascending=False)

    plt.figure(figsize=(8, 6))
    sns.barplot(x='Importance', y='Features', data=feature_df, palette="coolwarm")
    plt.title('Feature Importance')
    plt.xlabel('Importance')
    plt.ylabel('Features')
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'feature_importance.png'))
    plt.close()
    
    # Save the trained model (Optional)
    import joblib
    joblib.dump(random_forest, 'media/social_media_addiction_model.pkl')

    # Pass accuracy to the template
    return render(request, 'users/accuracy.html', {
        'accuracy': accuracy,
        'confusion_matrix_img': 'media/confusion_matrix.png',
        'feature_importance_img': 'media/feature_importance.png'
 
        })


def Prediction(request):
    if request.method == "POST":
        # Retrieve input values from the form
        whatsapp = float(request.POST.get('whatsapp'))
        instagram = float(request.POST.get('instagram'))
        snapchat = float(request.POST.get('snapchat'))
        telegram = float(request.POST.get('telegram'))
        facebook = float(request.POST.get('facebook'))
        bereal = float(request.POST.get('bereal'))
        tiktok = float(request.POST.get('tiktok'))
        wechat = float(request.POST.get('wechat'))
        twitter = float(request.POST.get('twitter'))
        linkedin = float(request.POST.get('linkedin'))
        messages = float(request.POST.get('messages'))
        total_time = float(request.POST.get('total_time'))
        hourly_open = int(request.POST.get('hourly_open'))

        # Create input data array
        input_data = np.array([[whatsapp, instagram, snapchat, telegram, facebook, bereal, tiktok, wechat, twitter, linkedin, messages, total_time, hourly_open]])

        # Load trained model (ensure the model is saved correctly)
        model = joblib.load('media/social_media_addiction_model.pkl')

        # Predict
        prediction = model.predict(input_data)
        result = 'Addicted' if prediction[0] == 1 else 'Not Addicted'

        # Save behavior tracking data if user is logged in
        if 'id' in request.session:
            user_id = request.session['id']
            user = UserRegistrationModel.objects.get(id=user_id)

            UserBehaviorTracking.objects.create(
                user=user,
                whatsapp=whatsapp,
                instagram=instagram,
                snapchat=snapchat,
                telegram=telegram,
                facebook=facebook,
                bereal=bereal,
                tiktok=tiktok,
                wechat=wechat,
                twitter=twitter,
                linkedin=linkedin,
                messages=messages,
                total_screen_time=total_time,
                hourly_opens=hourly_open,
                prediction_result=result
            )

        # Generate recommendations based on prediction and usage patterns
        recommendations = []

        if result == 'Addicted':
            if total_time > 20:
                recommendations.append("⏰ Your total screen time is very high. Try to limit it to under 3 hours per day.")

            if hourly_open > 100:
                recommendations.append("📱 You're checking your phone too frequently. Try to reduce unlocking to less than 50 times per day.")

            if instagram > 10 or tiktok > 10:
                recommendations.append("📸 Reduce social media scrolling time, especially Instagram and TikTok.")

            if whatsapp > 8:
                recommendations.append("💬 Limit WhatsApp usage. Set specific times to check messages instead of constant checking.")

            recommendations.append("🔕 Turn off non-essential notifications to reduce distractions.")
            recommendations.append("🌙 Enable Digital Wellbeing mode or Screen Time limits on your device.")
            recommendations.append("🧘 Take regular breaks. Follow the 20-20-20 rule: every 20 minutes, look at something 20 feet away for 20 seconds.")
            recommendations.append("📵 Create phone-free zones (bedroom, dining table) and times (before bed, during meals).")
        else:
            recommendations.append("✅ Great job! Your smartphone usage is healthy.")
            recommendations.append("💪 Keep maintaining this balanced approach to technology.")
            recommendations.append("🎯 Continue setting boundaries and being mindful of your screen time.")

            if total_time > 15:
                recommendations.append("⚠️ Your screen time is moderate. Try to keep it under 3 hours daily.")

        # Display the result in detection.html
        return render(request, 'users/detection.html', {
            'result': result,
            'recommendations': recommendations,
            'total_time': total_time,
            'hourly_open': hourly_open
        })

    return render(request, 'users/test_input.html')



def ViewDataset(request):
    dataset = os.path.join(settings.MEDIA_ROOT, 'Filtered_ClassSurvey.csv')
    import pandas as pd
    df = pd.read_csv(dataset,nrows=100)
    df = df.to_html(index=None)
    return render(request, 'users/viewData.html', {'data': df})


from django.shortcuts import render, redirect
from .models import UserRegistrationModel, UserBehaviorTracking, UserAlertSettings
from django.contrib import messages

def UserRegisterActions(request):
    if request.method == 'POST':
        # Check for missing required fields
        required_fields = ['name', 'loginid', 'password', 'mobile', 'email', 'locality', 'address', 'city', 'state']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]
        
        if missing_fields:
            messages.error(request, f"Missing required fields: {', '.join(missing_fields)}. Please update your form.")
            return render(request, 'UserRegistrations.html')

        try:
            user = UserRegistrationModel(
                name=request.POST.get('name'),
                loginid=request.POST.get('loginid'),
                password=request.POST.get('password'),
                mobile=request.POST.get('mobile'),
                email=request.POST.get('email'),
                locality=request.POST.get('locality'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                status='waiting'
            )
            user.save()
            messages.success(request, "Registration successful!")
            return redirect('UserLogin') # Redirect to login on success
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
            
    return render(request, 'UserRegistrations.html')


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                data = {'loginid': loginid}
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})

def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})


def index(request):
    return render(request,"index.html")


import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import UserRegistrationModel

otp_storage = {}  # Temporary dictionary to store OTPs

def send_otp(email):
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    otp_storage[email] = otp

    subject = "Password Reset OTP"
    message = f"Your OTP for password reset is: {otp}"
    from_email = "saikumardatapoint1@gmail.com"  # Change this to your email
    send_mail(subject, message, from_email, [email])

    return otp

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if UserRegistrationModel.objects.filter(email=email).exists():
            send_otp(email)
            request.session["reset_email"] = email  # Store email in session
            return redirect("verify_otp")
        else:
            messages.error(request, "Email not registered!")

    return render(request, "users/forgot_password.html")

def verify_otp(request):
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        email = request.session.get("reset_email")

        if otp_storage.get(email) and str(otp_storage[email]) == otp_entered:
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP!")

    return render(request, "users/verify_otp.html")

def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        email = request.session.get("reset_email")

        if UserRegistrationModel.objects.filter(email=email).exists():
            user = UserRegistrationModel.objects.get(email=email)
            user.password = new_password  # Updating password
            user.save()
            messages.success(request, "Password reset successful! Please log in.")
            return redirect("UserLoginCheck")

    return render(request, "users/reset_password.html")


def ModelComparison(request):
    # Load dataset
    data_set = pd.read_csv('media/ClassSurvey.csv')

    # Encode the target column
    encoder = LabelEncoder()
    data_set['SocialMediaAddiction'] = encoder.fit_transform(data_set['SocialMediaAddiction'])

    # Select relevant columns
    columns = [
        'Whatsapp', 'Instagram', 'Snapchat', 'Telegram', 'Facebook', 'BeReal',
        'TikTok', 'WeChat', 'Twitter', 'Linkedin', 'Messages',
        'TotalSocialMediaScreenTime', 'Number of times opened (hourly intervals)',
        'SocialMediaAddiction'
    ]
    df = data_set[columns]

    # Impute missing values
    imputer = SimpleImputer(strategy='mean')
    df[columns] = imputer.fit_transform(df[columns])

    # Prepare features and target variable
    X = df.drop('SocialMediaAddiction', axis=1)
    y = df['SocialMediaAddiction']

    # Apply SMOTE
    smote = SMOTE(random_state=42)
    X_balanced, y_balanced = smote.fit_resample(X, y)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

    # Define models
    models = {
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'SVM': SVC(random_state=42)
    }

    # Train and evaluate models
    results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        results.append({
            'model': name,
            'accuracy': round(accuracy * 100, 2),
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1 * 100, 2)
        })

    # Create comparison chart
    model_names = [r['model'] for r in results]
    accuracies = [r['accuracy'] for r in results]
    precisions = [r['precision'] for r in results]
    recalls = [r['recall'] for r in results]
    f1_scores = [r['f1_score'] for r in results]

    x = np.arange(len(model_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - 1.5*width, accuracies, width, label='Accuracy', color='#3498db')
    ax.bar(x - 0.5*width, precisions, width, label='Precision', color='#2ecc71')
    ax.bar(x + 0.5*width, recalls, width, label='Recall', color='#f39c12')
    ax.bar(x + 1.5*width, f1_scores, width, label='F1-Score', color='#e74c3c')

    ax.set_xlabel('Models', fontsize=12)
    ax.set_ylabel('Score (%)', fontsize=12)
    ax.set_title('Model Comparison - Performance Metrics', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'model_comparison.png'))
    plt.close()

    return render(request, 'users/model_comparison.html', {
        'results': results,
        'comparison_chart': 'media/model_comparison.png'
    })


def UserBehaviorHistory(request):
    if 'id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('UserLoginCheck')

    user_id = request.session['id']
    user = UserRegistrationModel.objects.get(id=user_id)

    # Get user's behavior history
    behavior_logs_all = UserBehaviorTracking.objects.filter(user=user).order_by('-date')

    if behavior_logs_all.count() == 0:
        return render(request, 'users/behavior_history.html', {
            'no_data': True,
            'message': 'No usage data found. Start tracking by making predictions!'
        })

    behavior_logs = behavior_logs_all[:30]

    # Prepare data for visualizations
    dates = [log.date.strftime('%Y-%m-%d') for log in behavior_logs]
    screen_times = [log.total_screen_time for log in behavior_logs]
    hourly_opens = [log.hourly_opens for log in behavior_logs]

    # Daily screen time trend
    plt.figure(figsize=(12, 5))
    plt.plot(dates, screen_times, marker='o', color='#3498db', linewidth=2)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Screen Time (hours)', fontsize=12)
    plt.title('Daily Screen Time Trend', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'screen_time_trend.png'))
    plt.close()

    # Phone unlocks trend
    plt.figure(figsize=(12, 5))
    plt.plot(dates, hourly_opens, marker='s', color='#e74c3c', linewidth=2)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Phone Unlocks', fontsize=12)
    plt.title('Daily Phone Unlock Frequency', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'phone_unlocks_trend.png'))
    plt.close()

    # App usage distribution (latest entry)
    latest_log = behavior_logs[0]
    apps = ['WhatsApp', 'Instagram', 'Snapchat', 'Telegram', 'Facebook', 'BeReal',
            'TikTok', 'WeChat', 'Twitter', 'LinkedIn', 'Messages']
    usage = [latest_log.whatsapp, latest_log.instagram, latest_log.snapchat,
             latest_log.telegram, latest_log.facebook, latest_log.bereal,
             latest_log.tiktok, latest_log.wechat, latest_log.twitter,
             latest_log.linkedin, latest_log.messages]

    # Filter out zero values
    filtered_data = [(app, use) for app, use in zip(apps, usage) if use > 0]
    if filtered_data:
        apps_filtered, usage_filtered = zip(*filtered_data)

        plt.figure(figsize=(10, 10))
        colors = plt.cm.Set3(range(len(apps_filtered)))
        plt.pie(usage_filtered, labels=apps_filtered, autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('App Usage Distribution (Latest)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(settings.MEDIA_ROOT, 'app_usage_distribution.png'))
        plt.close()

    # Weekly summary
    addicted_count = behavior_logs_all.filter(prediction_result='Addicted').count()
    not_addicted_count = behavior_logs_all.filter(prediction_result='Not Addicted').count()

    return render(request, 'users/behavior_history.html', {
        'behavior_logs': list(behavior_logs[:10]),
        'screen_time_chart': 'media/screen_time_trend.png',
        'phone_unlocks_chart': 'media/phone_unlocks_trend.png',
        'app_distribution_chart': 'media/app_usage_distribution.png',
        'addicted_count': addicted_count,
        'not_addicted_count': not_addicted_count,
        'total_logs': behavior_logs_all.count()
    })


def AlertSettings(request):
    if 'id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('UserLoginCheck')

    user_id = request.session['id']
    user = UserRegistrationModel.objects.get(id=user_id)

    # Get or create alert settings
    alert_settings, created = UserAlertSettings.objects.get_or_create(
        user=user,
        defaults={
            'screen_time_limit': 5.0,
            'unlock_limit': 80,
            'social_media_limit': 3.0,
            'alerts_enabled': True
        }
    )

    if request.method == 'POST':
        alert_settings.screen_time_limit = float(request.POST.get('screen_time_limit'))
        alert_settings.unlock_limit = int(request.POST.get('unlock_limit'))
        alert_settings.social_media_limit = float(request.POST.get('social_media_limit'))
        alert_settings.alerts_enabled = request.POST.get('alerts_enabled') == 'on'
        alert_settings.save()
        messages.success(request, 'Alert settings updated successfully!')

    # Check latest behavior log for alerts
    alerts = []
    latest_log = UserBehaviorTracking.objects.filter(user=user).order_by('-timestamp').first()

    if latest_log and alert_settings.alerts_enabled:
        if latest_log.total_screen_time > alert_settings.screen_time_limit:
            alerts.append({
                'type': 'danger',
                'icon': '⏰',
                'message': f'Screen time alert! You have used your phone for {latest_log.total_screen_time} hours today. Limit: {alert_settings.screen_time_limit} hours.'
            })

        if latest_log.hourly_opens > alert_settings.unlock_limit:
            alerts.append({
                'type': 'warning',
                'icon': '📱',
                'message': f'Phone unlock alert! You have unlocked your phone {latest_log.hourly_opens} times. Limit: {alert_settings.unlock_limit} times.'
            })

        social_media_total = (latest_log.instagram + latest_log.facebook +
                             latest_log.tiktok + latest_log.snapchat + latest_log.twitter)
        if social_media_total > alert_settings.social_media_limit:
            alerts.append({
                'type': 'info',
                'icon': '📸',
                'message': f'Social media alert! You have spent {social_media_total:.1f} hours on social media. Limit: {alert_settings.social_media_limit} hours.'
            })

        if latest_log.prediction_result == 'Addicted':
            alerts.append({
                'type': 'danger',
                'icon': '⚠️',
                'message': 'Addiction risk detected! Your usage pattern indicates smartphone addiction. Please review recommendations.'
            })

    return render(request, 'users/alert_settings.html', {
        'alert_settings': alert_settings,
        'alerts': alerts,
        'latest_log': latest_log
    })

