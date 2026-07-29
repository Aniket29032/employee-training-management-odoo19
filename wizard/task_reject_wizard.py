# -*- coding: utf-8 -*-

from odoo import _, fields, models


class TaskRejectWizard(models.TransientModel):
    _name = "task.reject.wizard"
    _description = "Reject Training Task"

    task_id = fields.Many2one(
        "project.task",
        required=True,
    )

    review_comment = fields.Html(
        string="Rejection Reason",
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()

        task = self.task_id

        task.write({
            "training_status": "in_progress",
            "is_rejected": True,
            "review_comment": self.review_comment,
            "reviewed_on": fields.Datetime.now(),
            "reviewed_by": self.env.user.id,
        })

        task.activity_unlink([
            "mail.mail_activity_data_todo"
        ])

        # Notify trainee
        if task.user_ids:

            task.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=task.user_ids[0].id,
                summary=_("Training Task Rejected"),
                note=self.review_comment,
            )

        task.message_post(
            body=_(
                "Task rejected by <b>%s</b>."
            ) % self.env.user.name
        )

        return {
            "type": "ir.actions.act_window_close"
        }