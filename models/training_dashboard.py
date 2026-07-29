# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TrainingDashboard(models.Model):
    _name = "et.training.dashboard"
    _description = "Training Dashboard"
    _auto = False


    course_count = fields.Integer(
        string="Courses",
        compute="_compute_dashboard",
    )

    session_count = fields.Integer(
        string="Sessions",
        compute="_compute_dashboard",
    )

    trainer_count = fields.Integer(
        string="Trainers",
        compute="_compute_dashboard",
    )

    trainee_count = fields.Integer(
        string="Trainees",
        compute="_compute_dashboard",
    )

    attendance_count = fields.Integer(
        string="Attendance",
        compute="_compute_dashboard",
    )

    certificate_count = fields.Integer(
        string="Certificates",
        compute="_compute_dashboard",
    )

    pending_review_count = fields.Integer(
        string="Pending Reviews",
        compute="_compute_dashboard",
    )

    draft_courses = fields.Integer(
        compute="_compute_dashboard",
    )

    running_courses = fields.Integer(
        compute="_compute_dashboard",
    )

    completed_courses = fields.Integer(
        compute="_compute_dashboard",
    )

    cancelled_courses = fields.Integer(
        compute="_compute_dashboard",
    )

    assigned_tasks = fields.Integer(
        compute="_compute_dashboard",
    )

    submitted_tasks = fields.Integer(
        compute="_compute_dashboard",
    )

    approved_tasks = fields.Integer(
        compute="_compute_dashboard",
    )

    rejected_tasks = fields.Integer(
        compute="_compute_dashboard",
    )

    @api.depends()
    def _compute_dashboard(self):

        Course = self.env["et.course"]
        Session = self.env["et.session"]
        Attendance = self.env["et.session.attendance"]
        Certificate = self.env["et.course.certificate"]
        Employee = self.env["hr.employee"]
        Task = self.env["project.task"]

        for rec in self:

            rec.course_count = Course.search_count([])

            rec.session_count = Session.search_count([])

            rec.trainer_count = Employee.search_count([
                ("is_trainer", "=", True)
            ])

            rec.trainee_count = Employee.search_count([])

            rec.attendance_count = Attendance.search_count([])

            rec.certificate_count = Certificate.search_count([])

            rec.pending_review_count = Task.search_count([
                ("training_status", "=", "submitted")
            ])

            rec.draft_courses = Course.search_count([
                ("state", "=", "draft")
            ])

            rec.running_courses = Course.search_count([
                ("state", "=", "in_progress")
            ])

            rec.completed_courses = Course.search_count([
                ("state", "=", "done")
            ])

            rec.cancelled_courses = Course.search_count([
                ("state", "=", "cancel")
            ])

            rec.assigned_tasks = Task.search_count([
                ("training_status", "=", "assigned")
            ])

            rec.submitted_tasks = Task.search_count([
                ("training_status", "=", "submitted")
            ])

            rec.approved_tasks = Task.search_count([
                ("training_status", "=", "approved")
            ])

            rec.rejected_tasks = Task.search_count([
                ("training_status", "=", "rejected")
            ])

    @api.model
    def search(self, domain=None, offset=0, limit=None, order=None):
        return self.browse([1])

    @api.model
    def read(self, fields=None, load="_classic_read"):
        return super().browse([1]).read(fields, load)

    def init(self):
        pass