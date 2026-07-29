# -*- coding: utf-8 -*-

from odoo import fields, models


class ETCourseTag(models.Model):
    _name = "et.course.tags"
    _description = "Course Tags"
    _order = "name"

    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )

    code = fields.Char(
        string="Code",
        tracking=True,
    )