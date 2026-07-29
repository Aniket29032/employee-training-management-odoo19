# -*- coding: utf-8 -*-

from odoo import fields, models


class TrainingActivity(models.Model):
    _name = "et.training.activity"
    _description = "Training Activity Timeline"
    _order = "create_date desc"

    task_id = fields.Many2one(
        "project.task",
        string="Task",
        required=True,
        ondelete="cascade",
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
    )

    user_id = fields.Many2one(
        "res.users",
        string="Performed By",
        default=lambda self: self.env.user,
        readonly=True,
    )

    activity_type = fields.Selection(
        [
            ("assigned", "Task Assigned"),
            ("started", "Work Started"),
            ("submitted", "Work Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Activity",
        required=True,
    )

    description = fields.Html(
        string="Description",
    )