# -*- coding: utf-8 -*-
{
    "name": "Employee Training Management",
    "version": "19.0.1.0.0",
    "summary": "Employee Training Management System",
    "description": """
Employee Training Management
============================

Manage employee training courses, sessions,
attendance, trainers, certificates and reporting.
""",
    "category": "Human Resources",
    "author": "Your Name",
    "website": "",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
        "project",
    ],
    "data": [
        "security/employee_training_security.xml",
        'security/security.xml',
        "security/training_record_rules.xml",
        "security/ir.model.access.csv",


        "data/sequence.xml",
        "data/certificate_sequence.xml",
        "data/mail_template.xml",

        

        "wizard/create_task_wizard_views.xml",
        "wizard/task_reject_wizard_views.xml",
        "wizard/attendance_wizard_views.xml",
        

        "reports/certificate_report.xml",
        "reports/certificate_template.xml",

        "views/et_course_tag_views.xml",
        "views/et_course_views.xml",
        "views/et_session_views.xml",
        "views/et_session_attendance_views.xml",
        "views/hr_employee_views.xml",
        "views/et_course_certificate_views.xml",
        "views/et_course_analysis_views.xml",
        "views/et_reject_wizard_views.xml",
        "views/project_task_views.xml",
        "views/training_contacts_views.xml",
        "views/hr_employee_training_views.xml",
        "views/menu_views.xml",


        
        ],
    "demo": [],
    "installable": True,
    "application": True,
}