from odoo import fields, models


class ETRejectWizard(models.TransientModel):
    _name = "et.reject.wizard"
    _description = "Reject Wizard"

    reason = fields.Text(
        string="Reason",
        required=True,
    )

    def action_confirm_reject(self):
        active_id = self.env.context.get("active_id")
        active_model = self.env.context.get("active_model")

        if active_model and active_id:

            record = self.env[active_model].browse(active_id)

            record.write({
                "state": "cancel",
                "reject_reason": self.reason,
            })

            record.message_post(
                body=f"<b>Rejected</b><br/>Reason:<br/>{self.reason}"
            )

        return {
            "type": "ir.actions.act_window_close",
        }