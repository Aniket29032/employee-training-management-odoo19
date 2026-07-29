# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class ETSession(models.Model):
    _name = "et.session"
    _description = "Training Session"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Session",
        required=True,
        tracking=True,
    )

    course_id = fields.Many2one(
        comodel_name="et.course",
        string="Course",
        required=True,
        ondelete="cascade",
        tracking=True,
    )

    trainer_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Trainer",
        domain=[("is_trainer", "=", True)],
        tracking=True,
    )

    trainee_employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Trainees",
    )


    session_start_time = fields.Datetime(
        string="Start",
        tracking=True,
    )

    session_end_time = fields.Datetime(
        string="End",
        tracking=True,
    )

   
    attendance_ids = fields.One2many(
        "et.session.attendance",
        "session_id",
        string="Attendance",
        tracking=True,
    )

    attendance_sheet_count = fields.Integer(
    compute="_compute_attendance_sheet_count",
)

    task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="training_session_id",
        string="Tasks",
    )

    attendance_count = fields.Integer(
        string="Attendance",
        compute="_compute_counts",
    )

    trainee_count = fields.Integer(
        string="Trainees",
        compute="_compute_counts",
    )

    task_count = fields.Integer(
        string="Tasks",
        compute="_compute_counts",
    )

    state = fields.Selection(
    [
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("done", "Completed"),
        ("cancel", "Cancelled"),
    ],
    string="Status",
    default="draft",
    tracking=True,
)

    is_training_employee = fields.Boolean(
        compute="_compute_is_training_employee",
    )

    current_employee_id = fields.Many2one(
        "hr.employee",
        compute="_compute_current_employee",
    )

    is_training_admin = fields.Boolean(
        compute="_compute_is_training_admin",
    )

    def action_start_session(self):
        for session in self:

        # ---------------------------------------
        # Validation : already started
        # ---------------------------------------
            if session.session_start_time:
                raise UserError(
                    _("This session has already been started.")
                )

        # ---------------------------------------
        # Validation : at least one trainee
        # ---------------------------------------
            if not session.trainee_employee_ids:
                raise UserError(
                 _("Please add at least one trainee before starting the session.")
                )

        # ---------------------------------------
        # Start Session
        # ---------------------------------------
            session.write({
                "session_start_time": fields.Datetime.now(),
                "state": "in_progress",
            })

        # ---------------------------------------
        # Start Course automatically
        # ---------------------------------------
            if session.course_id.state == "draft":
                session.course_id.action_start()

    def action_create_tasks(self):
        self.ensure_one()

    # Validation: Session should be started
        if self.state == "draft":
            raise UserError(
                _("Please start the session before creating tasks.")
            )

    # Validation: Session should not be cancelled
        if self.state == "cancel":
            raise UserError(
                _("You cannot create tasks for a cancelled session.")
            )

    # Validation: Project should exist
        if not self.course_id.project_id:
            raise UserError(
                _("Please create a project for this course first.")
            )

    # Validation: At least one trainee should exist
        if not self.trainee_employee_ids:
            raise UserError(
                _("Please add at least one trainee.")
            )

        return {
            "type": "ir.actions.act_window",
            "name": "Create Tasks",
            "res_model": "et.create.task.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_session_id": self.id,
            },
        }
    


    def _compute_counts(self):
        task_obj = self.env["project.task"]

        for session in self:
            session.attendance_count = len(session.attendance_ids)
            session.trainee_count = len(session.trainee_employee_ids)

            session.task_count = task_obj.search_count([
                ("training_session_id", "=", session.id)
            ])


    def action_view_attendance(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Attendance",
            "res_model": "et.session.attendance",
            "view_mode": "list,form",
            "domain": [("session_id", "=", self.id)],
            "context": {
                "default_session_id": self.id,
                "default_course_id": self.course_id.id,
            },
        }
    
    def action_view_trainees(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Trainees",
            "res_model": "hr.employee",
            "view_mode": "list,form",
            "domain": [("id", "in", self.trainee_employee_ids.ids)],
        }

    def action_view_tasks(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Tasks",
            "res_model": "project.task",
            "view_mode": "list,form",
            "domain": [("training_session_id", "=", self.id)],
        }
    
    def action_complete_session(self):
        for session in self:

        # Validation: Session must be started first
            if not session.session_start_time:
                raise UserError(
                    _("Please start the session before completing it.")
                )

        # Validation: Session should not be completed twice
            if session.state == "done":
                raise UserError(
                    _("This session has already been completed.")
                )

        # Complete the session
            session.write({
                "session_end_time": fields.Datetime.now(),
                "state": "done",
            })

        # Automatically complete the course if all active sessions are completed
            active_sessions = session.course_id.session_ids.filtered(
                lambda s: s.state != "cancel"
            )

            if active_sessions and all(s.state == "done" for s in active_sessions):
                session.course_id.action_done()

        

        


    def action_cancel_session(self):
        self.write({
            "state": "cancel",
        })


    @api.constrains("trainer_employee_id", "trainee_employee_ids")
    def _check_trainer_not_trainee(self):
        for session in self:

            if (
                session.trainer_employee_id
                and session.trainer_employee_id in session.trainee_employee_ids
            ):
                raise ValidationError(
                    _("Trainer cannot be selected as a trainee.")
                )
            
    def _compute_is_training_employee(self):
        employee = self.env.user.employee_id

        for session in self:
            session.is_training_employee = (
                employee in session.trainee_employee_ids
            )

    def _compute_current_employee(self):
        employee = self.env.user.employee_id

        for session in self:
            session.current_employee_id = employee


    @api.depends_context("uid")
    def _compute_is_training_admin(self):
        for record in self:
            record.is_training_admin = self.env.user.has_group(
                "employee_training_management.group_training_admin"
            )


    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)

        if self.env.user.has_group(
            "employee_training_management.group_training_trainer"
        ) and not self.env.user.has_group(
            "employee_training_management.group_training_admin"
        ):
            employee = self.env["hr.employee"].search(
                [("user_id", "=", self.env.user.id)],
                limit=1,
            )

            if employee:
                vals["trainer_employee_id"] = employee.id

        return vals

    @api.constrains("trainer_employee_id")
    def _check_trainer_assignment(self):
        for session in self:

            if self.env.user.has_group(
                "employee_training_management.group_training_admin"
            ):
                continue

            if self.env.user.has_group(
                "employee_training_management.group_training_trainer"
            ):

                employee = self.env["hr.employee"].search(
                    [("user_id", "=", self.env.user.id)],
                    limit=1,
                )

                if (
                    session.trainer_employee_id
                    and session.trainer_employee_id != employee
                ):
                    raise ValidationError(
                        _("You can only assign yourself as trainer.")
                    )


    


    def action_create_attendance_sheet(self):
        self.ensure_one()

        if self.state == "draft":
            raise UserError(
                _("Please start the session first.")
            )

        if self.state == "cancel":
            raise UserError(
                _("Cannot create attendance for a cancelled session.")
            )

        today = fields.Date.context_today(self)

        existing_sheet = self.env["et.attendance.sheet"].search([
            ("session_id", "=", self.id),
            ("attendance_date", "=", today),
        ], limit=1)

        if existing_sheet:
            raise UserError(
                _("Attendance sheet for today has already been created.")
            )

        attendance_sheet = self.env["et.attendance.sheet"].create({
            "session_id": self.id,
            "attendance_date": fields.Date.context_today(self),
        })

        attendance_lines = []

        for trainee in self.trainee_employee_ids:
            attendance_lines.append({
                "attendance_sheet_id": attendance_sheet.id,
                "trainee_employee_id": trainee.id,
                "course_id": self.course_id.id,
                "session_id": self.id,
                "status": "present",
            })

        self.env["et.session.attendance"].create(attendance_lines)

        return {
            "type": "ir.actions.act_window",
            "res_model": "et.attendance.sheet",
            "res_id": attendance_sheet.id,
            "view_mode": "form",
            "target": "current",
        }


    def action_open_attendance_wizard(self):
        self.ensure_one()

        if self.state != "in_progress":
            raise UserError(
                _("Attendance can only be taken while the session is In Progress.")
            )   

        wizard = self.env["et.attendance.wizard"].create({
            "session_id": self.id,
            "attendance_date": fields.Date.context_today(self),
        })

        return {
            "type": "ir.actions.act_window",
            "name": _("Take Attendance"),
            "res_model": "et.attendance.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
        }