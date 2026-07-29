from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AttendanceWizard(models.TransientModel):
    _name = "et.attendance.wizard"
    _description = "Take Attendance"

    session_id = fields.Many2one(
        "et.session",
        required=True,
        readonly=True,
    )


    attendance_date = fields.Date(
    string="Attendance Date",
    required=True,
    default=fields.Date.context_today,
    )

    line_ids = fields.One2many(
        "et.attendance.wizard.line",
        "wizard_id",
        string="Attendance",
    )

    @api.constrains("attendance_date")
    def _check_attendance_date(self):
        today = fields.Date.context_today(self)

        for rec in self:
            if rec.attendance_date != today:
                raise ValidationError(
                    _("Attendance can only be taken for today's date.")
                )

    @api.model
    def create(self, vals):
        wizard = super().create(vals)

        session = wizard.session_id

        if session.state != "in_progress":
            raise ValidationError(
                _("Attendance can only be taken while session is In Progress.")
            )

        for trainee in session.trainee_employee_ids:
            self.env["et.attendance.wizard.line"].create({
                "wizard_id": wizard.id,
                "trainee_employee_id": trainee.id,
                "status": "present",
            })

        return wizard

    def action_save_attendance(self):

        self.ensure_one()

    # ---------------------------------------
    # Validation : Only today's attendance
    # ---------------------------------------
        today = fields.Date.context_today(self)

        if self.attendance_date != today:
            raise ValidationError(
                _("Attendance can only be taken for today's date.")
            )   

        Attendance = self.env["et.session.attendance"]

    # ---------------------------------------
    # Validation : Attendance already exists
    # ---------------------------------------
        existing = Attendance.search_count([
            ("session_id", "=", self.session_id.id),
            ("attendance_date", "=", self.attendance_date),
        ])

        if existing:
            raise ValidationError(
                _("Attendance for %s has already been taken.")
                % self.attendance_date
            )

    # ---------------------------------------
    # Create Attendance
    # ---------------------------------------
        attendance_values = []

        for line in self.line_ids:
            attendance_values.append({
                "session_id": self.session_id.id,
                "course_id": self.session_id.course_id.id,
                "trainee_employee_id": line.trainee_employee_id.id,
                "attendance_date": self.attendance_date,
                "status": line.status,
            })

        Attendance.create(attendance_values)

        return {
            "type": "ir.actions.act_window_close"
        }