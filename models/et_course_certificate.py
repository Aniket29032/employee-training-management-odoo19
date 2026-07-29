# -*- coding: utf-8 -*-

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ETCourseCertificate(models.Model):
    _name = "et.course.certificate"
    _description = "Course Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Certificate Number",
        readonly=True,
        copy=False,
        default="New",
        tracking=True,
    )

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        tracking=True,
    )

    course_id = fields.Many2one(
        comodel_name="et.course",
        string="Course",
        required=True,
        tracking=True,
    )

    issue_date = fields.Date(
        string="Issue Date",
        default=fields.Date.today,
        tracking=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=True,
    )

    responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        default=lambda self: self.env.user,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "et.course.certificate"
                ) or "New"

        return super().create(vals_list)

    _sql_constraints = [
        (
            "unique_employee_course",
            "unique(employee_id, course_id)",
            "A certificate already exists for this employee and course.",
        ),
    ]

    def action_send_certificate_email(self):
        self.ensure_one()

        if not self.employee_id.work_email:
            raise UserError(
                _("Employee does not have a work email.")
            )

        # Email Template
        template = self.env.ref(
            "employee_training_management.mail_template_training_certificate"
        )

        # Generate PDF Report
        pdf_content, _ = self.env["ir.actions.report"]._render_qweb_pdf(
            "employee_training_management.action_report_training_certificate",
            [self.id],
        )

        # Create Attachment
        attachment = self.env["ir.attachment"].create({
            "name": f"{self.name}.pdf",
            "type": "binary",
            "datas": base64.b64encode(pdf_content),
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "application/pdf",
        })

        # Attach PDF to Email
        template.attachment_ids = [(6, 0, [attachment.id])]

        # Send Email
        template.send_mail(
            self.id,
            force_send=True,
        )

        # Remove Attachment from Template
        template.attachment_ids = [(5, 0, 0)]

        return {
        "type": "ir.actions.client",
        "tag": "display_notification",
        "params": {
            "title": _("Success"),
            "message": _(
                "Certificate has been emailed successfully to %s."
            ) % self.employee_id.work_email,
            "type": "success",
            "sticky": False,
        },
    }