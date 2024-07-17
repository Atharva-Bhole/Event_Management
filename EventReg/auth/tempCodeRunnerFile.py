@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/reset-password')
def reset_password():
    return render_template('reset-password.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/events')
def events():
    return 'events.html'

@app.route('/calendar')
def calendar():
    return 'calendar.html'
