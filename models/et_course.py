# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from markupsafe import Markup



class ETCourse(models.Model):
    _name = "et.course"
    _description = "Employee Training Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "id desc"

    name = fields.Char(
        string="Course",
        required=True,
        tracking=True,
    )

    number = fields.Char(
        string="Number",
        readonly=True,
        copy=False,
        default="New",
        tracking=True,
    )

    tag_ids = fields.Many2many(
        comodel_name="et.course.tags",
        string="Tags",
    )

    course_index = fields.Binary(
        string="Course Index",
        attachment=True,
        tracking=True,
    )

    duration_days = fields.Integer(
        string="Duration (Days)",
        required=True,
        tracking=True,
    )

    index_ids = fields.One2many(
        comodel_name="et.course.index",
        inverse_name="course_id",
        string="Index",
    )

    session_ids = fields.One2many(
        comodel_name="et.session",
        inverse_name="course_id",
        string="Sessions",
        readonly=True,
    )

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        readonly=True,
        copy=False,
    )

    certificate_ids = fields.One2many(
        comodel_name="et.course.certificate",
        inverse_name="course_id",
        string="Certificates",
        readonly=True,
    )

    certificate_count = fields.Integer(
        compute="_compute_counts",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("cancel", "Cancelled"),
            ("done", "Done"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    session_count = fields.Integer(
    compute="_compute_counts",
    )

    trainer_count = fields.Integer(
        compute="_compute_counts",
    )

    trainee_count = fields.Integer(
        compute="_compute_counts",
    )

    attendance_count = fields.Integer(
        compute="_compute_counts",
    )

    task_count = fields.Integer(
        compute="_compute_counts",
    )

    project_count = fields.Integer(
        string="Project",
        compute="_compute_counts",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )

    training_cost = fields.Monetary(
        string="Training Cost",
        currency_field="currency_id",
        tracking=True,
    )

    reject_reason = fields.Text(
        string="Reject Reason",
        readonly=True,
        tracking=True,
    )

    is_training_employee = fields.Boolean(
        compute="_compute_current_employee",
    )

    current_employee_id = fields.Many2one(
        "hr.employee",
        compute="_compute_current_employee",
    )

    

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("number", "New") == "New":
                vals["number"] = self.env["ir.sequence"].next_by_code("et.course") or "New"

        return super().create(vals_list)
    
    def action_start(self):
        for course in self:

            if not course.index_ids:
                raise UserError(_("Please add at least one Course Index before starting the course."))

            # Remove old sessions so the course can be reused
            course.session_ids.unlink()

            for index in course.index_ids.sorted("sequence"):

                self.env["et.session"].create({
                    "name": index.name,
                    "course_id": course.id,
                })

            course.state = "in_progress"


    def action_done(self):
        for course in self:

        # Validation: At least one session should exist
            if not course.session_ids:
                raise UserError(
                    _("Please create at least one session before completing the course.")
                )

        # Validation: All active sessions must be completed
            pending_sessions = course.session_ids.filtered(
                lambda session: session.state not in ("done", "cancel")
            )

            if pending_sessions:
                raise UserError(
                    _("All active sessions must be completed before completing the course.")
                )

            course.state = "done"


    def action_cancel(self):
        self.write({
            "state": "cancel",
        })


    def action_set_to_draft(self):
        self.write({
            "state": "draft",
        })


    def unlink(self):
        for record in self:
            if record.state not in ("draft", "cancel"):
                raise UserError(
                    _("Only Draft or Cancelled records can be deleted.")
                )
        return super().unlink()
    
    def action_create_project(self):
        for course in self:

            if course.project_id:
                raise UserError(_("Project already exists for this course."))

            project = self.env["project.project"].create({
                "name": course.name,
            })

            course.project_id = project.id


    def action_view_project(self):
        self.ensure_one()

        if not self.project_id:
            raise UserError(_("No project found."))

        return {
            "type": "ir.actions.act_window",
            "name": "Project",
            "res_model": "project.project",
            "view_mode": "form",
            "res_id": self.project_id.id,
            "target": "current",
        }   


    def _compute_counts(self):
        attendance_obj = self.env["et.session.attendance"]
        task_obj = self.env["project.task"]

        for course in self:

            sessions = course.session_ids

            course.session_count = len(sessions)

            course.trainer_count = len(
                sessions.mapped("trainer_employee_id")
            )

            course.trainee_count = len(
                sessions.mapped("trainee_employee_ids")
            )

            course.attendance_count = attendance_obj.search_count([
                ("course_id", "=", course.id)
            ])

            course.task_count = task_obj.search_count([
                ("training_session_id.course_id", "=", course.id)
            ])    

            course.project_count = 1 if course.project_id else 0

            course.certificate_count = len(course.certificate_ids)

    def action_view_sessions(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Sessions",
            "res_model": "et.session",
            "view_mode": "list,form",
            "domain": [("course_id", "=", self.id)],
        }
    
    def action_view_trainers(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Trainers",
            "res_model": "hr.employee",
            "view_mode": "list,form",
            "domain": [
                ("id", "in", self.session_ids.mapped("trainer_employee_id").ids)
            ],
        }
    
    def action_view_trainees(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Trainees",
            "res_model": "hr.employee",
            "view_mode": "list,form",
            "domain": [
                ("id", "in", self.session_ids.mapped("trainee_employee_ids").ids)
            ],
        }
    

    def action_view_attendance(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Attendance",
            "res_model": "et.session.attendance",
            "view_mode": "list,form",
            "domain": [("course_id", "=", self.id)],
        }
    
    def action_view_tasks(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Tasks",
            "res_model": "project.task",
            "view_mode": "list,form",
            "domain": [
                ("training_session_id.course_id", "=", self.id)
            ],
        }

    def action_view_certificates(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Certificates",
            "res_model": "et.course.certificate",
            "view_mode": "list,form",
            "domain": [("course_id", "=", self.id)],
        }
    
    def action_generate_certificates(self):
        self.ensure_one()

        if self.state != "done":
            raise UserError(
                _("Certificates can only be generated for completed courses.")
            )

        trainees = self.session_ids.mapped("trainee_employee_ids")

        if not trainees:
            raise UserError(
                _("No trainees found for this course.")
            )

        certificate_obj = self.env["et.course.certificate"]
        task_obj = self.env["project.task"]

        created_count = 0

        for trainee in trainees:

            # Find trainee's training task(s) for this course
            task = task_obj.search([
                ("project_id", "=", self.project_id.id),
                ("user_ids", "in", trainee.user_id.id),
            ], limit=1)

            # Skip if task doesn't exist or isn't approved
            if not task or task.training_status != "approved":
                continue

        # Skip if certificate already exists
            existing = certificate_obj.search([
                ("course_id", "=", self.id),
                ("employee_id", "=", trainee.id),
            ], limit=1)

            if existing:
                continue

            certificate_obj.create({
                "employee_id": trainee.id,
                "course_id": self.id,
            })

            created_count += 1

        if not created_count:
            raise UserError(
                _(
                    "No certificates were generated.\n\n"
                    "Certificates can only be generated for trainees whose training tasks have been approved."
                )
            )

    def action_send_certificates(self):
        self.ensure_one()

        template = self.env.ref(
            "employee_training_management.mail_template_training_certificate"
        )

        for certificate in self.certificate_ids:

            if not certificate.employee_id.work_email:
                continue

            template.send_mail(
                certificate.id,
                force_send=True,
            )


    def action_open_reject_wizard(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Reject",
            "res_model": "et.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.id,
                "active_model": self._name,
            },
        }
    

    def action_set_to_draft(self):
        for record in self:
            record.write({
                "state": "draft",
                "reject_reason": False,
            })

            record.message_post(
                body=Markup(
                    "<b>Course moved back to Draft.</b><br/>"
                    "The rejection reason has been cleared."
                )
            )


    @api.depends_context("uid")
    def _compute_current_employee(self):

        employee = self.env.user.employee_id

        for course in self:

            course.current_employee_id = employee

            course.is_training_employee = bool(
                employee
                and course.session_ids.filtered(
                    lambda s: employee in s.trainee_employee_ids
                )
            )