# -*- coding: utf-8 -*-

from odoo import fields, models


class ETSessionAttendance(models.Model):
    _name = "et.session.attendance"
    _description = "Training Session Attendance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "attendance_date desc, id desc"

    session_id = fields.Many2one(
        comodel_name="et.session",
        string="Session",
        required=True,
        ondelete="cascade",
        tracking=True,
    )

    course_id = fields.Many2one(
        comodel_name="et.course",
        string="Course",
        related="session_id.course_id",
        store=True,
        readonly=True,
    )

    trainer_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Trainer",
        related="session_id.trainer_employee_id",
        store=True,
        readonly=True,
    )

    trainee_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Trainee",
        required=True,
        tracking=True,
    )

    attendance_date = fields.Date(
        string="Attendance Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )

    status = fields.Selection(
        [
            ("present", "Present"),
            ("absent", "Absent"),
        ],
        string="Status",
        default="present",
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        (
            "unique_session_trainee_date",
            "unique(session_id, trainee_employee_id, attendance_date)",
            "Attendance for this trainee has already been taken for this date.",
        ),
    ]

    def action_toggle_status(self):
        for rec in self:
            rec.status = (
                "absent"
                if rec.status == "present"
                else "present"
            )