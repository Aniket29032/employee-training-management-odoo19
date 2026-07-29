from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_trainer = fields.Boolean(
        string="Trainer",
        tracking=True,
    )

    is_training_admin = fields.Boolean(
        string="Training Administrator",
        tracking=True,
    )

    is_trainee = fields.Boolean(
    string="Trainee",
    default=True,
    tracking=True,
)

    training_session_count = fields.Integer(
    compute="_compute_training_counts",
)

    training_task_count = fields.Integer(
    compute="_compute_training_counts",
)

    training_attendance_count = fields.Integer(
    compute="_compute_training_counts",
)

    training_certificate_count = fields.Integer(
    compute="_compute_training_counts",
)

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        employees.with_context(skip_training_user_sync=True)._create_training_user()
        return employees

    def write(self, vals):
        res = super().write(vals)

        if not self.env.context.get("skip_training_user_sync"):
            self._sync_training_user()

        return res

    def _create_training_user(self):

        Users = self.env["res.users"].sudo()

        employee_group = self.env.ref(
            "employee_training_management.group_training_employee"
        )

        trainer_group = self.env.ref(
            "employee_training_management.group_training_trainer"
        )

        admin_group = self.env.ref(
            "employee_training_management.group_training_admin"
        )

        for employee in self:

            if employee.user_id:
                self._update_training_groups(
                    employee.user_id,
                    employee_group,
                    trainer_group,
                    admin_group,
                    employee,
                )
                continue

            if not employee.work_email:
                raise ValidationError(_(
                    "Please enter Work Email. A user account is automatically created for every employee."
                ))

            user = Users.search(
                [("login", "=", employee.work_email)],
                limit=1,
            )

            if not user:
                user = Users.create({
                    "name": employee.name,
                    "login": employee.work_email,
                    "email": employee.work_email,
                })

            employee.with_context(
                skip_training_user_sync=True
            ).write({
                "user_id": user.id,
            })

            self._update_training_groups(
                user,
                employee_group,
                trainer_group,
                admin_group,
                employee,
            )

    def _sync_training_user(self):

        employee_group = self.env.ref(
            "employee_training_management.group_training_employee"
        )

        trainer_group = self.env.ref(
            "employee_training_management.group_training_trainer"
        )

        admin_group = self.env.ref(
            "employee_training_management.group_training_admin"
        )

        for employee in self:

            user = employee.user_id

            if not user:
                continue

            vals = {}

            if employee.name != user.name:
                vals["name"] = employee.name

            if employee.work_email:

                if employee.work_email != user.login:
                    vals["login"] = employee.work_email

                if employee.work_email != user.email:
                    vals["email"] = employee.work_email

            if vals:
                user.write(vals)

            self._update_training_groups(
                user,
                employee_group,
                trainer_group,
                admin_group,
                employee,
            )

    def _update_training_groups(
        self,
        user,
        employee_group,
        trainer_group,
        admin_group,
        employee,
    ):

        commands = [
            (3, employee_group.id),
            (3, trainer_group.id),
            (3, admin_group.id),

            # Every employee automatically gets Employee role
            (4, employee_group.id),
        ]

        # Trainer
        if employee.is_trainer:
            commands.append((4, trainer_group.id))

        # Training Administrator
        if employee.is_training_admin:

            # Admin should always have Trainer rights too
            if not employee.is_trainer:
                commands.append((4, trainer_group.id))

            commands.append((4, admin_group.id))

        user.write({
            "group_ids": commands,
        })


        # ============================================================
# COMPUTE SMART BUTTON COUNTS
# ============================================================

    def _compute_training_counts(self):

        Session = self.env["et.session"].sudo()
        Attendance = self.env["et.session.attendance"].sudo()
        Certificate = self.env["et.course.certificate"].sudo()
        Task = self.env["project.task"].sudo()

        for employee in self:

        # Sessions
            if employee.is_trainer:
                employee.training_session_count = Session.search_count([
                    ("trainer_employee_id", "=", employee.id)
                ])
            else:
                employee.training_session_count = Session.search_count([
                    ("trainee_employee_ids", "in", employee.id)
                ])

        # Attendance
            employee.training_attendance_count = Attendance.search_count([
                ("trainee_employee_id", "=", employee.id)
            ])

        # Certificates
            employee.training_certificate_count = Certificate.search_count([
                ("employee_id", "=", employee.id)
            ])

        # Tasks
            if employee.user_id:
                employee.training_task_count = Task.search_count([
                    ("user_ids", "in", employee.user_id.id)
                ])
            else:
                employee.training_task_count = 0


# ============================================================
# SMART BUTTONS
# ============================================================

    def action_view_training_sessions(self):
        self.ensure_one()

        if self.is_trainer:
            domain = [("trainer_employee_id", "=", self.id)]
        else:
            domain = [("trainee_employee_ids", "in", self.id)]

        return {
            "type": "ir.actions.act_window",
            "name": _("Training Sessions"),
            "res_model": "et.session",
            "view_mode": "list,form",
            "domain": domain,
        }


    def action_view_training_tasks(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Training Tasks"),
            "res_model": "project.task",
            "view_mode": "list,form",
            "domain": [("user_ids", "in", self.user_id.id)],
        }


    def action_view_training_attendance(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Attendance"),
            "res_model": "et.session.attendance",
            "view_mode": "list,form",
            "domain": [
                ("trainee_employee_id", "=", self.id)
            ],
        }


    def action_view_training_certificates(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": _("Certificates"),
            "res_model": "et.course.certificate",
            "view_mode": "list,form",
            "domain": [
                ("employee_id", "=", self.id)
            ],
        }