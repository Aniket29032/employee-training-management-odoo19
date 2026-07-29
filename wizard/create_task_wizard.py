# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import UserError
from markupsafe import Markup


class CreateTaskWizard(models.TransientModel):
    _name = "et.create.task.wizard"
    _description = "Create Training Tasks"

    session_id = fields.Many2one(
        "et.session",
        required=True,
    )

    task_title = fields.Char(
        string="Task Title",
        required=True,
    )

    task_description = fields.Html(
        string="Task Description",
        required=True,
    )

    def action_create_tasks(self):
        self.ensure_one()

        session = self.session_id

    # Validation: Session should be started
        if session.state == "draft":
            raise UserError(
                _("Please start the session before creating tasks.")
            )

    # Validation: Cancelled session
        if session.state == "cancel":
            raise UserError(
                _("You cannot create tasks for a cancelled session.")
            )

        if not session.course_id.project_id:
            raise UserError(_("Please create project first."))

        if not session.trainee_employee_ids:
            raise UserError(_("Please select trainees."))

        existing_tasks = self.env["project.task"].search([
            ("training_session_id", "=", session.id)
        ])

        if existing_tasks:
            raise UserError(_("Tasks already exist for this session."))

        todo_activity = self.env.ref("mail.mail_activity_data_todo")

        for trainee in session.trainee_employee_ids:

            task = self.env["project.task"].create({
                "name": f"{self.task_title} - {trainee.name}",
                "description": self.task_description,
                "project_id": session.course_id.project_id.id,
                "training_session_id": session.id,
                "user_ids": [(6, 0, trainee.user_id.ids)],
            })

        # --------------------------------------------------
        # Inbox Notification
        # --------------------------------------------------

            task.message_post(
            subject=_("Training Task Assigned"),
            body=Markup("""
                <b>New Training Task Assigned</b><br/>
                <b>Course:</b> %s<br/>
                <b>Session:</b> %s<br/><br/>
                Please complete your assigned task before the deadline.
            """) % (
                session.course_id.name,
                session.name,
            ),
        )

        # --------------------------------------------------
        # Activity
        # --------------------------------------------------

            task.activity_schedule(
                activity_type_id=todo_activity.id,
                user_id=trainee.user_id.id,
                note=_(
                    "Please complete your assigned training task."
                ),
            )

        return {"type": "ir.actions.act_window_close"}