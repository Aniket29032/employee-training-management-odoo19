# -*- coding: utf-8 -*-

from odoo import fields, models


class ETAttendanceWizardLine(models.TransientModel):
    _name = "et.attendance.wizard.line"
    _description = "Attendance Wizard Line"

    wizard_id = fields.Many2one(
        "et.attendance.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )

    trainee_employee_id = fields.Many2one(
        "hr.employee",
        string="Trainee",
        required=True,
        readonly=True,
    )

    status = fields.Selection(
        [
            ("present", "Present"),
            ("absent", "Absent"),
        ],
        string="Status",
        default="present",
        required=True,
    )