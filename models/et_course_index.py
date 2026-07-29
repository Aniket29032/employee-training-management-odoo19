# -*- coding: utf-8 -*-

from odoo import fields, models


class ETCourseIndex(models.Model):
    _name = "et.course.index"
    _description = "Course Index"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, id"

    sequence = fields.Integer(
        string="Sequence",
       
    )

    name = fields.Char(
        string="Chapter",
        required=True,
        tracking=True,
    )

    course_id = fields.Many2one(
        comodel_name="et.course",
        string="Course",
        required=True,
        ondelete="cascade",
    )