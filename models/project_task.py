# -*- coding: utf-8 -*-
from datetime import date
from odoo import _, fields, models
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = "project.task"

    training_session_id = fields.Many2one(
        comodel_name="et.session",
        string="Training Session",
        ondelete="cascade",
    )

    training_status = fields.Selection(
        [
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Training Status",
        default="assigned",
        tracking=True,
    )

    submission_file = fields.Binary(
        string="Submission File",
        attachment=True,
    )

    submission_filename = fields.Char(
        string="File Name",
    )

    submission_note = fields.Html(
        string="Submission Notes",
    )

    submitted_on = fields.Datetime(
        string="Submitted On",
        readonly=True,
    )

    reviewed_on = fields.Datetime(
        string="Reviewed On",
        readonly=True,
    )

    reviewed_by = fields.Many2one(
        "res.users",
        string="Reviewed By",
        readonly=True,
    )

    review_comment = fields.Html(
        string="Review Comment",
    )

    is_rejected = fields.Boolean(
        string="Rejected",
        default=False,
    )

    

    def action_start_work(self):
        for task in self:

            if task.training_status != "assigned":
                raise UserError(_("Only assigned tasks can be started."))

            task.training_status = "in_progress"

    def action_submit_work(self):

        if self.env.user.has_group(
            "employee_training_management.group_training_trainer"
        ) or self.env.user.has_group(
            "employee_training_management.group_training_admin"
        ):
            raise UserError(_("Only trainees can submit training work."))
        for task in self:

            if not task.submission_file:
                raise UserError(
                    _("Please upload your work before submitting.")
                )

           
            task.write({
                "training_status": "submitted",
                "submitted_on": fields.Datetime.now(),
                "is_rejected": False,
            })

            trainer = task.training_session_id.trainer_employee_id.user_id

            if trainer:

                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=trainer.id,
                    summary=_("Training Task Submitted"),
                    note=_(
                        "<p><b>%s</b> has submitted the training task.</p>"
                        "<p>Please review the submission.</p>"
                    ) % task.name,
                    date_deadline=date.today(),
                )

    def action_approve_work(self):
        for task in self:

            if task.training_status != "submitted":
                raise UserError(_("Only submitted work can be approved."))

            task.write({
                "training_status": "approved",
                "reviewed_on": fields.Datetime.now(),
                "reviewed_by": self.env.user,
            })

            task.activity_unlink(
            ["mail.mail_activity_data_todo"]
        )

    def action_reject_work(self):
        self.ensure_one()

        if self.training_status != "submitted":
            raise UserError(
                _("Only submitted work can be rejected.")
            )

        return {
            "type": "ir.actions.act_window",
            "name": _("Reject Submission"),
            "res_model": "task.reject.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_task_id": self.id,
            },
        }     